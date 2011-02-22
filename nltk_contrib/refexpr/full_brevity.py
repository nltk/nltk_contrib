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

from util import validate_facts, Type, Rel, generate_phrase

class FullBrevity:
  """
  Implementation of the "full brevity" referring expression algorithm from Dale and Haddock 1991.
  """
  def __init__(self, facts):
    """
    Initializes class with a set of facts about objects in the world (see example method).
    facts is expected to be a list with each element being a list of the form:
      [fact category, fact name, object id]

    fact category may be Type or a user-defined name.
    fact name may be any string.
    object id must be a unique identifer for a given object.
    """
    self.facts = facts
    self.object_ids = validate_facts(self.facts)
    assert not any(map(lambda f: f == Rel, self.facts)), "Full Brevity does not support relationships"

  def describe(self, target_id):
    """
    Returns a list of facts that uniquely identify an object or None if no such
    description is possible.
    """
    assert target_id in self.object_ids, "No facts for %s" % target_id
    description = []

    # List of attribute/value dictionaries for every distractor object
    distractors = [dict([(f[0], f) for f in self.facts if f[2] == o_id]) for o_id in self.object_ids.difference([target_id])]

    # Attribute/value pairs for the target object
    properties = dict([(f[0], f) for f in self.facts if f[2] == target_id])

    while len(distractors) > 0:
      if len(properties) == 0:
        # No unique description is possible
        return None

      best_set = None
      best_prop = None

      # Find the property that best constrains the distractors set
      for prop_key in properties.keys():
        prop_val = properties[prop_key]
        dist_set = [dist for dist in distractors if dist[prop_key][1] == prop_val[1]]
        if (best_set is None) or (len(dist_set) < len(best_set)):
          best_set = dist_set
          best_prop = prop_val

      # Update description
      description.append(best_prop)
      properties.pop(best_prop[0])
      distractors = best_set
    
    return description

  @staticmethod
  def example():
    """Example of using the FullBrevity class."""
    facts = [[Type, "cube", "obj1"], ["color", "red", "obj1"], ["size", "big", "obj1"],
             [Type, "ball", "obj2"], ["color", "blue", "obj2"], ["size", "big", "obj2"],
             [Type, "ball", "obj3"], ["color", "red", "obj3"], ["size", "small", "obj3"]]

    fb = FullBrevity(facts)

    # Print English description for each object
    for obj_id in ["obj1", "obj2", "obj3"]:
      obj_type = [f for f in facts if f[0] == Type and f[2] == obj_id] # Include type for clarity
      print "%s: %s" % (obj_id, generate_phrase(fb.describe(obj_id) + obj_type, ["color", "size"]))

