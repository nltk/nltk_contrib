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

import constraint
from copy import copy, deepcopy
from util import validate_facts, Type, Rel, generate_phrase_rel

class _RelationalVar:
  """Internal class used to represent relational variables"""
  fresh_var_id = 0

  def __init__(self, var_id):
    self.var_id = var_id

  def __eq__(self, other):
    return self.var_id == other.var_id

  def __repr__(self):
    return "<_RelationalVar %s>" % self.var_id

  def __str__(self):
    return str(self.var_id)

  def __hash__(self):
    return hash(self.var_id)

  @staticmethod
  def get_fresh_var():
    _RelationalVar.fresh_var_id += 1
    return _RelationalVar(_RelationalVar.fresh_var_id - 1)


class Relational:
  """
  Implementation of the "relational" referring expression algorithm from Dale and Haddock 1991.
  """
  def __init__(self, facts):
    """
    Initializes class with a set of facts about objects in the world (see example method).
    facts is expected to be a list with each element being a list of the form:
      [fact category, fact name, object id, ...]

    fact category may be Type, Rel, or a user-defined name.
    fact name may be any string.
    object id must be a unique identifer for a given object.
    ... = more object ids if fact category is Rel
    """
    self.facts = deepcopy(facts)
    self.object_ids = validate_facts(self.facts)
    self.object_ids_list = list(self.object_ids)

  def __make_constraint(self, fact, var_arg_map):
    """Returns a function constraint that maps parameter values onto fact's variables"""
    return lambda *args: (fact[:2] + [args[var_arg_map[fact_part.var_id]] if isinstance(fact_part, _RelationalVar) else fact_part for fact_part in fact[2:]]) in self.facts

  def __get_facts_for(self, obj_id):
    """Returns all unused facts about obj_id"""
    return [fact for fact in self.facts if (not fact in self.used_facts) and any([fact_id == obj_id for fact_id in fact[2:]])]

  def __fact_replace(self, fact, to_replace, replace_with):
    """Replaces all occurrences of to_replace in fact with replace_with"""
    return fact[:2] + map(lambda fact_id: replace_with if (not isinstance(fact_id, _RelationalVar) and fact_id == to_replace) else fact_id, fact[2:])

  def __get_context_set(self, constraints, obj_var):
    """Returns a set of objects that fit the given constraints for obj_var"""
    network_var = str(obj_var)
    variables = set([obj_var] + [var for cst in constraints for var in cst[0][2:]])
    network = constraint.Problem()

    for var in variables:
      network.addVariable(str(var), self.object_ids_list)

    for cst in constraints:
      network.addConstraint(self.__make_constraint(cst[0], cst[1]), cst[2])

    solutions = network.getSolutions()
    return set([soln[network_var] for soln in solutions])

  def describe(self, target_id):
    """
    Returns a list of facts that uniquely identify an object or None if no such
    description is possible.
    """
    self.used_facts = []
    description = []
    var_obj_map = {}

    assert target_id in self.object_ids, "No facts for %s" % target_id

    # Initial state, goal is to describe target_id
    obj_id = target_id
    obj_var = _RelationalVar.get_fresh_var()
    var_obj_map[obj_var] = obj_id
    network_var = str(obj_var)
    goal_stack = [(obj_id, obj_var)]
    obj_facts_dict = {obj_id: self.__get_facts_for(obj_id)}
    constraints = []

    while len(goal_stack) > 0:
      obj_id, obj_var = goal_stack[len(goal_stack) - 1]
      network_var = str(obj_var)
      var_set = self.__get_context_set(constraints, obj_var)

      if len(var_set) == 0:
        # No unique description is possible
        return None

      if len(var_set) == 1:
        goal_stack.pop()
        continue

      obj_facts = obj_facts_dict[obj_id]

      assert len(obj_facts) > 0, "Ran out of facts for %s" % obj_id

      # Find the "best" fact -- the one that most constrains the object set
      best_fact = None
      best_soln_size = len(var_set)

      for fact in obj_facts:
        test_fact = self.__fact_replace(fact, obj_id, obj_var)
        test_soln_set = self.__get_context_set(constraints + [(test_fact, {obj_var.var_id: 0}, [network_var])], obj_var)

        if (len(test_soln_set) < best_soln_size):
          best_fact = fact
          best_soln_size = len(test_soln_set)

      # If no best fact is found (i.e. the set was not constrained any further), then
      # we should abandon this sub-goal. If we're on top of the stack, though, FAIL.
      if best_fact is None:
        goal_stack.pop()
        assert len(goal_stack) > 0, "No unique description is possible for %s" % obj_id
        continue

      obj_facts.remove(best_fact)
      self.used_facts.append(best_fact) # Avoid infinite loop

      # Replace constant portions of the best fact with variables
      best_fact = self.__fact_replace(best_fact, obj_id, obj_var)
      best_net_vars = [network_var]
      best_var_map = {obj_var.var_id: 0}

      for other_id in [fact_part for fact_part in best_fact[2:] if not isinstance(fact_part, _RelationalVar)]:
        other_var = _RelationalVar.get_fresh_var()
        var_obj_map[other_var] = other_id
        other_net_var = str(other_var)
        goal_stack.append((other_id, other_var)) # Add new goal to the stack
        obj_facts_dict[other_id] = self.__get_facts_for(other_id)

        # Prepare for constraint
        best_fact = self.__fact_replace(best_fact, other_id, other_var)
        best_net_vars.append(other_net_var)
        best_var_map[other_var.var_id] = len(best_net_vars) - 1

      # Update text description and network constraints
      description.append(best_fact[:2] + [var_obj_map[v] for v in best_fact[2:]])
      constraints.append((best_fact, best_var_map, best_net_vars))

    return description

  @staticmethod
  def example():
    """Example of using the Relational class."""
    facts = [[Type, "cup", "c1"], [Type, "cup", "c2"], [Type, "cup", "c3"],
             [Type, "bowl", "b1"], [Type, "bowl", "b2"],
             [Type, "table", "t1"], [Type, "table", "t2"], ["color", "red", "t2"],
             [Type, "floor", "f1"],
             [Rel, "in", "c1", "b1"], [Rel, "in", "c2", "b2"],
             [Rel, "on", "c3", "f1"], [Rel, "on", "b1", "f1"], [Rel, "on", "b2", "t1"],
             [Rel, "on", "t1", "f1"], [Rel, "on", "t2", "f1"]]

    rel = Relational(facts)
    obj_types = [f for f in facts if f[0] == Type] # Include types in the description for clarity
    handlers = {
      "on" : lambda(lr): "on" if lr else "on which lies",
      "in" : lambda(lr): "in" if lr else "in which lies"
    }

    # Generate an English description for each object
    for obj_id in ["c1", "c2", "c3", "b1", "b2", "t1", "t2", "f1"]:
      print "%s: %s" % (obj_id, generate_phrase_rel(rel.describe(obj_id) + obj_types, ["color"], obj_id, handlers))

