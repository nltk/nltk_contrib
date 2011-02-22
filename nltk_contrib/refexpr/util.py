# Copyright 2010 Rebecca Ingram, Michael Hansen, Jason Yoder
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class _Type:
  """Internal class used to mark Type facts"""
  def __repr__(self):
    return "Type"

  def __eq__(self, other):
    return isinstance(other, self.__class__)

  def __ne__(self, other):
    return not self.__eq__(other)

  def __hash__(self):
    return hash(0)

class _Rel:
  """Internal class used to mark Rel facts"""
  def __repr__(self):
    return "Rel"

  def __eq__(self, other):
    return isinstance(other, self.__class__)

  def __ne__(self, other):
    return not self.__eq__(other)

  def __hash__(self):
    return hash(1)

Type = _Type() # Singleton Type object
Rel = _Rel() # Singleton Rel object

def validate_facts(facts):
  """
  Validates that a list of facts conform to expectations.
  Specifically:
    * Every object must have a Type fact
    * Type and predicate facts have fixed lengths
    * Rel facts have a minimum length

  Returns the set of object ids.
  """
  object_ids = set()
  objects_with_types = set()

  for f in facts:
    category = f[0] # First element is fact category

    if category == Type:
      assert len(f) == 3, "Type facts must be of the form [Type, type name, object id]"
      object_ids.add(f[2])
      objects_with_types.add(f[2])
    elif category == Rel:
      assert len(f) > 3, "Relational facts must be of the form [Rel, rel name, object id, object id, ...]"
      object_ids = object_ids.union(f[2:])
    else:
      assert len(f) == 3, "Predicate facts must be of the form [category, predicate name, object id]"
      object_ids.add(f[2])

  # All objects must have a type
  assert len(set.difference(object_ids, objects_with_types)) == 0, "All objects must have a Type fact"

  return object_ids

# Generate an English phrase from a description.
def generate_phrase(description, attr_prefs, handlers = None):
    if description == None:
        return "No disambiguating referring expression found."

    attrs = [f[0] for f in description]
    desc_dict = dict([(f[0], f[1]) for f in description])

    # Commenting this assertion because we don't want it for full brevity.
    # Instead, check if Type is included; if not, use "one" 
    #assert(attrs.count(Type) > 0)
    if attrs.count(Type) == 0:
        attrs.append(Type)
        desc_dict[Type] = "one"

    # Type always goes last
    attrs = [a for a in attrs if a != Type]
    attr_queue = [desc_dict[Type]]

    # Put the highest priority attributes next to the noun
    for attr in attr_prefs:
        if (attrs.count(attr) > 0):
            if (handlers != None) and (handlers.has_key(attr)):
                attr_queue.insert(0, handlers[attr](desc_dict[attr]))
            else:
              attr_queue.insert(0, desc_dict[attr])

            attrs.remove(attr)

    # Add the remaining attributes in the order we got them (farthest from 
    # the noun)
    for attr in attrs:
        attr_queue.insert(0, desc_dict[attr])

    return "the %s" % str.join(" ", attr_queue)

def generate_phrase_rel(description, attr_prefs, target_id, handlers = None, top_level = True):
  if description == None:
    return "No disambiguating referring expression found."
  #get the relational attributes of our referent
  target_rels = [f for f in description if f[0] == Rel and (f[2] == target_id or f[3] == target_id)]
  target_desc = generate_phrase([f for f in description if f[0] != Rel and f[2] == target_id], attr_prefs, handlers)

  #relational attributes are added after whatever other attributes are used in generating English
  if len(target_rels) == 0:
    return target_desc

  clauses = []
  
  if not top_level:
    target_rels = [target_rels[0]]
  
  #generate English for relational attributes
  for cur_rel in target_rels:
    #Define attributes that are not in the current description of the referent
    #and are not non-relational attributes that have the referent as their first object
    other_attrs = [f for f in description if f not in target_rels and not (f[0] != Rel and f[1] == target_id)]
    rel_desc = cur_rel[1]
   
    # We have to handle which position the referent is in the relational attribute
    # There is a difference between generating the phrases:
    # "the box on the table" and "the table on which the box sits"
    if cur_rel[2] == target_id:
      if (handlers != None) and (handlers.has_key(rel_desc)):
        rel_desc = handlers[rel_desc](True)

      other_desc = generate_phrase_rel(other_attrs, attr_prefs, cur_rel[3], handlers, False)
      clauses.append("%s %s %s" % (target_desc, rel_desc, other_desc))
    else:
      if (handlers != None) and (handlers.has_key(rel_desc)):
        rel_desc = handlers[rel_desc](False)

      other_desc = generate_phrase_rel(other_attrs, attr_prefs, cur_rel[2], handlers, False)
      clauses.append("%s %s %s" % (target_desc, rel_desc,  other_desc))
  #This simple construction of phrases seems to makes sense most of the time
  return str.join(", and is ", clauses)

