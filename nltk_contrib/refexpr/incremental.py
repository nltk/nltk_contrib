import string

from copy import copy, deepcopy
from util import validate_facts, Type, Rel, generate_phrase

class Incremental:
    """
    Implementation of the "incremental" referring expression algorithm from 
    Reiter and Dale (1992). 
    """
    def __init__(self, facts, ranked_attrs, taxonomy):
        """
        Initializes class with a set of facts about objects in the world (see 
            example method), a set of ranked attributes, and a taxonomy.
    
        facts is expected to be a list where each element is a list of the form:
            [fact category, fact name, object id, ...]

            fact category may be Type, or a user-defined name (all facts that 
                use Rel will be ignored for this algorithm).
            fact name may be any string.
            object id must be a unique identifier for a given object.
            ... = more object ids if fact category is Rel.

        ranked_attrs is expected to be a list of attributes in descending order
            of preference. Attributes may be either Type or user-defined names 
            used in the fact set above.
        
        taxonomy is expected to be a Taxonomy (or an object which implements the 
            methods listed in the Taxonomy documentation), which contains a 
            taxonomy for the fact names.
        """
        self.facts = deepcopy(facts)
        self.object_ids = validate_facts(self.facts)
        self.object_ids_list = list(self.object_ids)

        # TODO: may want to validate the attribute list and/or the taxonomy
        self.ranked_attrs = ranked_attrs
        self.tree = taxonomy
    
    def describe(self, target_id):
        """
        Returns a list of facts that distinguish the object from other objects 
        in the fact set.
        """
        description = []
        type_included = False
        assert target_id in self.object_ids, "No facts known for %s" % target_id

        distractor_ids = self.object_ids - set([target_id]) # set difference

        # Iterate through the preferred attributes in ranked order
        for cur_attr in self.ranked_attrs:
            cur_fact = [f for f in self.facts if f[0] == cur_attr and \
                    f[2] == target_id]

            # If the target has no value for this attribute in the fact set.
            if len(cur_fact) == 0:
                continue

            basic_val = self.tree.basic_level_value(target_id, cur_attr, \
                    cur_fact[0][1])
            best_val = self.find_best_value(target_id, cur_attr, basic_val, distractor_ids)

            # Did we find a good value?
            if(best_val != None):
                # If so, how many distractors are ruled out by it?
                dist_ruled_out = self.rules_out(cur_attr, best_val, distractor_ids)

                # Did we rule out at least one distractor?
                if len(dist_ruled_out) > 0:
                    description.append([cur_attr, best_val, target_id]) # non-destructive
                    distractor_ids = distractor_ids - set(dist_ruled_out) # set difference
                    if(cur_attr == Type):
                        type_included = True

            # Have all distractors been eliminated? If so, make sure type is
            # included in the description and return.
            if len(distractor_ids) == 0:
                # Make sure that the type is included in the description
                if not type_included:
                    type_included = True
                    type_fact = [f for f in self.facts if f[0] == Type and \
                            f[2] == target_id]
                    assert len(type_fact) > 0, \
                            "Object %s missing type attribute." % target_id
                    basic_val = self.tree.basic_level_value(target_id, Type,
                            type_fact[0][1])
                    description.append([Type, basic_val, target_id])
                return description

        # If there are still distractors, we didn't find a way to distinguish
        # the referent using the preferred attributes and the given fact set.
        if len(distractor_ids) > 0:
            return None
        return description

    def find_best_value(self, target_id, attr, initial_value, distractors):
        """
        Check the taxonomy, distractors, and fact set to determine the best 
        value for the attribute to describe the target_id.

        From the paper: return a value for the attribute that is subsumed by 
        the initial value, accurately describes the referent, rules out as 
        many distractors as possible, and, subject to these constraints, is
        as close as possible in the taxonomy to the initial value (where the
        initial "initial_value" is the basic level description).
        """

        # If there's no taxonomy, we can't generalize at all, so just return 
        # the initial value.
        if self.tree == None:
            return initial_value

        if self.tree.user_knows(target_id, attr, initial_value, self.facts) == True:
            value = initial_value
        else:
            value = None

        # For each child in the taxonomy, see if it rules out more distractors 
        # than the current best value.
        for child in self.tree.taxonomy_children(initial_value, attr):
            new_value = self.find_best_value(target_id, attr, child, distractors)
            len1 = len(self.rules_out(attr, new_value, distractors))
            len2 = len(self.rules_out(attr, value, distractors))
            
            attr_val = self.get_attribute_value(attr, target_id)
            if self.tree.subsumes(child, attr_val) and \
                    (not new_value == None) and (value == None or len1 > len2):
                value = new_value
        return value
    
    def rules_out(self, attr, value, distractors):
        """
        A distractor can be ruled out if the user knows that it does not have 
        the specified value for the attribute. (When user_knows returns false, 
        it does not meant that the user does not know; it means that the user 
        knows the description is false).
        """
        return [dist for dist in distractors \
                     if self.tree.user_knows(dist, attr, value, self.facts) == False]

    # TODO: We can probably make this more efficient if we sort and do a 
    # fancier search.
    def get_attribute_value(self, attrib, target_id):
        """
        Look up the value of an attribute for a target in the fact set.
        """
        for fact in self.facts:
            if (fact[0] == attrib) and (fact[1] == target_id):
                return fact[2]
        return None

    # Generate an English phrase from a description.
    def generate_phrase(self, description, attr_prefs=None):
        if attr_prefs == None:
            attr_prefs = self.ranked_attrs

        return util.generate_phrase(description, attr_prefs)

    @staticmethod
    def example():
        """Example of using the Incremental class."""
        facts = [[Type, "cube", "obj1"], ["color", "brick", "obj1"], ["size", "big", "obj1"],
                 [Type, "ball", "obj2"], ["color", "navy", "obj2"], ["size", "big", "obj2"],
                 [Type, "ball", "obj3"], ["color", "scarlet", "obj3"], ["size", "small", "obj3"]]

        ranked_attrs = ["color", "size", Type]
        tax = {
            "blue" : {"parent" : None, "children" : ["navy", "cerulean"]},
            "red"  : {"parent" : None, "children" : ["scarlet", "brick"]},
            "navy" : {"parent" : "blue", "children" : []},
            "cerulean" : {"parent" : "blue", "children" : []},
            "scarlet" : {"parent" : "red", "children" : []},
            "brick" : {"parent" : "red", "children" : []}
        }

        taxonomy = Taxonomy(tax)
        incr = Incremental(facts, ranked_attrs, taxonomy)

        # Print English description for each object
        for obj_id in ["obj1", "obj2", "obj3"]:
            obj_type = [f for f in facts if f[0] == Type and f[2] == obj_id] # Include type for clarity
            print "%s: %s" % (obj_id, generate_phrase(incr.describe(obj_id) + obj_type, ["color", "size"]))


class Taxonomy:
    """
    Class for storing a taxonomy. May be overridden, or different classes 
    may be used in place. All that is required is that these functions are 
    defined: basic_level_value, user_knows, taxonomy_children, subsumes.

    In this implementation, all words are stored in a dictionary, and each 
    entry is itself a dictionary with optional entries for a basic level 
    value, a parent, and a list of children. Refer to the example() method 
    in the Incremental class for a demonstration.
    """
    def __init__(self, tree={}):
        self.lookup = tree

    def basic_level_value(self, obj, attr, value, facts=None, user=None):
        """
        Look up the value in the lookup table. If it has a basic value entry 
        (called basic), then return that. Otherwise, return its parent. If it 
        has no parent, just return the original value. The set of known facts
        and a user are included as optional arguments but aren't used in this
        implementation.
        """
        
        # Make sure value isn't None before we start trying to look it up
        if value == None:
            return value

        if value in self.lookup:
            value_info = self.lookup[value]
            if "basic" in value_info:
                return value_info["basic"]
            else:
                parent = self.get_parent(value)
                if parent == None:
                    return value
                else:
                    return parent
        else:
            return value
    
    def taxonomy_children(self, initial_value, attrib):
        """
        Look up a value in the taxonomy, and return a list of all of its
        children. Return the empty list either if value is not in the taxonomy
        or if it has no children.
        """
        value_info = self.lookup.get(initial_value, None)
        if value_info == None:
            return []
        else:
            return value_info.get("children", [])

    def user_knows(self, object, attr, value, facts, user=None):
        """
        Takes an object, an attribute, a value, a fact set, and a user
        
        Returns true if the user knows that the object has the value for that
            attribute (currently, this happens when either the object has that
            attribute value or if value subsumes the object's value for that
            attribute in the taxonomy)
        Returns false if the user knows that the object does not have the value 
            for that attribute.
        Returns None if the user doesn't know anything about the value of that
            attribute for the object.
        
        In this implementation, we assume that the user knows everything that 
            is in the fact set
        """
        specific_val = None
        val_found = False
        i = 0
        while not val_found and i < len(facts):
            if facts[i][0] == attr and facts[i][2] == object:
                val_found = True
                specific_val = facts[i][1]
            i += 1

        # if no value for object/attr is found, the user knows nothing
        if not val_found:
            return None

        # if value subsumes the specific value of the object, return true
        if self.subsumes(value, specific_val):
            return True
        else:
            return False

    def subsumes(self, parent, child):
        """
        Does the parent value subsume the child value: Check if child is a
        descendant of parent in the tree.
        """
        if child == None:
            return False

        if parent == child:
            return True

        # See if child is in the taxonomy and either recur on its parent (if it
        # has one) or return False.
        if child in self.lookup:
            # Get the child's parent, and see if it is subsumed by the parent
            # value that was passed in. 
            return self.subsumes(parent, self.get_parent(child))

        # If child is not in the taxonomy
        else:
            return False

    def get_parent(self, child):
        """
        Return the parent of child in the taxonomy (if it has one). If the
        child is not in the taxonomy or has no parent, return None.
        """
        if (child == None) or (not child in self.lookup):
            return None

        child_node = self.lookup[child]
        if "parent" in child_node:
            return child_node["parent"]
        else:
            return None

