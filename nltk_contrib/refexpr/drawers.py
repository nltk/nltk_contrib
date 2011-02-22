from random import shuffle
from full_brevity import *
from relational import *
from incremental import *
from util import generate_phrase, generate_phrase_rel

if __name__ == '__main__':
  # This data is based on the drawer pictures from Vienthen and Dale (2006)
  # Drawers are numbered (oddly) from left to right on even rows and right to left on odd rows (top to bottom)
  facts = [
    # Row 1
    [Type, "drawer", "d1"], ["color", "blue", "d1"],
    ["row", "1", "d1"], ["col", "1", "d1"], ["corner", "true", "d1"],
    [Rel, "above", "d1", "d8"], [Rel, "left", "d1", "d2"],
    [Rel, "above", "d1", "d9"], [Rel, "left", "d1", "d3"],
    [Rel, "above", "d1", "d16"], [Rel, "left", "d1", "d4"],

    [Type, "drawer", "d2"], ["color", "orange", "d2"],
    ["row", "1", "d2"], ["col", "2", "d2"], ["corner", "false", "d2"],
    [Rel, "above", "d2", "d7"], [Rel, "left", "d2", "d3"], [Rel, "right", "d2", "d1"],
    [Rel, "above", "d2", "d10"], [Rel, "left", "d2", "d4"], [Rel, "above", "d2", "d15"],

    [Type, "drawer", "d3"], ["color", "pink", "d3"],
    ["row", "1", "d3"], ["col", "3", "d3"], ["corner", "false", "d3"],
    [Rel, "above", "d3", "d6"], [Rel, "left", "d3", "d4"], [Rel, "right", "d3", "d2"],
    [Rel, "above", "d3", "d11"], [Rel, "right", "d3", "d1"], [Rel, "above", "d3", "d14"],

    [Type, "drawer", "d4"], ["color", "yellow", "d4"],
    ["row", "1", "d4"], ["col", "4", "d4"], ["corner", "true", "d4"],
    [Rel, "above", "d4", "d5"], [Rel, "right", "d4", "d3"],
    [Rel, "above", "d4", "d12"], [Rel, "right", "d4", "d2"],
    [Rel, "above", "d4", "d13"], [Rel, "right", "d4", "d1"],

    # Row 2
    [Type, "drawer", "d5"], ["color", "pink", "d5"],
    ["row", "2", "d5"], ["col", "4", "d5"], ["corner", "false", "d5"],
    [Rel, "above", "d5", "d12"], [Rel, "below", "d5", "d4"],
    [Rel, "above", "d5", "d13"], [Rel, "right", "d5", "d6"], [Rel, "right", "d5", "d7"],  [Rel, "right", "d5", "d8"],

    [Type, "drawer", "d6"], ["color", "yellow", "d6"],
    ["row", "2", "d6"], ["col", "3", "d6"], ["corner", "false", "d6"],
    [Rel, "above", "d6", "d11"], [Rel, "left", "d6", "d5"], [Rel, "right", "d6", "d7"], [Rel, "below", "d6", "d3"],
    [Rel, "above", "d6", "d14"], [Rel, "right", "d6", "d8"],

    [Type, "drawer", "d7"], ["color", "blue", "d7"],
    ["row", "2", "d7"], ["col", "2", "d7"], ["corner", "false", "d7"],
    [Rel, "above", "d7", "d10"], [Rel, "left", "d7", "d6"], [Rel, "right", "d7", "d8"], [Rel, "below", "d7", "d2"],
    [Rel, "above", "d7", "d15"], [Rel, "left", "d7", "d5"], 

    [Type, "drawer", "d8"], ["color", "blue", "d8"],
    ["row", "2", "d8"], ["col", "1", "d8"], ["corner", "false", "d8"],
    [Rel, "above", "d8", "d9"], [Rel, "left", "d8", "d7"], [Rel, "below", "d8", "d1"],
    [Rel, "above", "d8", "d16"], [Rel, "left", "d8", "d6"], [Rel, "left", "d8", "d5"],

    # Row 3
    [Type, "drawer", "d9"], ["color", "orange", "d9"],
    ["row", "3", "d9"], ["col", "1", "d9"], ["corner", "false", "d9"],
    [Rel, "above", "d9", "d16"], [Rel, "left", "d9", "d10"], [Rel, "below", "d9", "d8"],
    [Rel, "left", "d9", "d11"], [Rel, "left", "d9", "d12"], [Rel, "below", "d9", "d1"],

    [Type, "drawer", "d10"], ["color", "blue", "d10"],
    ["row", "3", "d10"], ["col", "2", "d10"], ["corner", "false", "d10"],
    [Rel, "above", "d10", "d15"], [Rel, "left", "d10", "d11"], [Rel, "right", "d10", "d9"], [Rel, "below", "d10", "d7"],
    [Rel, "left", "d10", "d12"], [Rel, "below", "d10", "d2"],

    [Type, "drawer", "d11"], ["color", "yellow", "d11"],
    ["row", "3", "d11"], ["col", "3", "d11"], ["corner", "false", "d11"],
    [Rel, "above", "d11", "d14"], [Rel, "left", "d11", "d12"], [Rel, "right", "d11", "d10"], [Rel, "below", "d11", "d6"],
    [Rel, "right", "d11", "d9"], [Rel, "below", "d11", "d3"],

    [Type, "drawer", "d12"], ["color", "orange", "d12"],
    ["row", "3", "d12"], ["col", "4", "d12"], ["corner", "false", "d12"],
    [Rel, "above", "d12", "d13"], [Rel, "right", "d12", "d11"], [Rel, "below", "d12", "d5"],
    [Rel, "right", "d12", "d10"], [Rel, "right", "d12", "d9"], [Rel, "below", "d12", "d4"],

    # Row 4
    [Type, "drawer", "d13"], ["color", "pink", "d13"],
    ["row", "4", "d13"], ["col", "4", "d13"], ["corner", "true", "d13"],
    [Rel, "below", "d13", "d12"], [Rel, "right", "d13", "d14"],
    [Rel, "below", "d13", "d5"], [Rel, "right", "d13", "d15"],
    [Rel, "below", "d13", "d4"], [Rel, "right", "d13", "d16"],

    [Type, "drawer", "d14"], ["color", "orange", "d14"],
    ["row", "4", "d14"], ["col", "3", "d14"], ["corner", "false", "d14"],
    [Rel, "below", "d14", "d11"], [Rel, "left", "d14", "d13"], [Rel, "right", "d14", "d15"],
    [Rel, "below", "d14", "d6"], [Rel, "right", "d14", "d16"], [Rel, "below", "d14", "d3"], 

    [Type, "drawer", "d15"], ["color", "pink", "d15"],
    ["row", "4", "d15"], ["col", "2", "d15"], ["corner", "false", "d15"],
    [Rel, "below", "d15", "d10"], [Rel, "left", "d15", "d14"], [Rel, "right", "d15", "d16"],
    [Rel, "below", "d15", "d7"], [Rel, "below", "d15", "d2"], [Rel, "left", "d15", "d13"],

    [Type, "drawer", "d16"], ["color", "yellow", "d16"],
    ["row", "4", "d16"], ["col", "1", "d16"], ["corner", "true", "d16"],
    [Rel, "below", "d16", "d9"], [Rel, "left", "d16", "d15"],
    [Rel, "below", "d16", "d1"], [Rel, "left", "d16", "d14"],
    [Rel, "below", "d16", "d8"], [Rel, "left", "d16", "d13"]
  ]

  #These are the data collected from subjects in Viethen and Dale's work. (2006)
  human_facts = {
    1: [
      [["color", "blue", "d1"], ["row", "1", "d1"], ["col", "1", "d1"], ["corner", "true", "d1"]],
      [["row", "1", "d1"], ["col", "1", "d1"], ["corner", "true", "d1"]],
      [["row", "1", "d2"], ["col", "2", "d2"]]
    ],

    2: [
      [["color", "orange", "d2"], ["col", "2", "d2"]],
      [["color", "orange", "d2"], ["row", "1", "d2"]],
      [["color", "orange", "d2"], [Rel, "above", "d2", "d7"],  ["color", "blue", "d7"]],
      [["col", "2", "d2"], ["row", "1", "d2"]],
      [["color", "orange", "d2"], ["col", "2", "d2"]],
      [["row", "1", "d2"], ["col", "2", "d2"]],
    ],

    3: [
      [["color", "pink", "d3"], ["row", "1", "d3"]],
      [["color", "pink", "d3"], ["row", "1", "d3"]],
      [["color", "pink", "d3"], ["row", "1", "d3"], ["col", "3", "d3"]],
      [["row", "1", "d3"], ["col", "3", "d3"]],
      [["color", "pink", "d3"], ["row", "1", "d3"]],
      [["color", "pink", "d3"], ["row", "1", "d3"]],
      [["color", "pink", "d3"], ["row", "1", "d3"]],
      [["row", "1", "d3"], ["col", "3", "d3"]],
    ],

    4: [
      [["row", "1", "d4"], ["col", "4", "d4"], ["corner", "true", "d4"]],
      [["color", "yellow", "d4"], ["row", "1", "d4"], ["col", "4", "d4"], ["corner", "true", "d4"]],
      [["col", "4", "d4"], ["row", "1", "d4"]],
      [["row", "1", "d4"], ["col", "3", "d4"]],
      [["row", "1", "d4"], ["col", "3", "d4"]],
      [["row", "1", "d4"], ["col", "4", "d4"], ["corner", "true", "d4"]],
      [["row", "1", "d4"], ["col", "3", "d4"]],
      [["row", "1", "d4"], ["col", "3", "d4"]],
    ],

    5: [
      [["color", "yellow", "d4"], [Rel, "above", "d4", "d5"], ["color", "pink", "d5"]],
      [["color", "pink", "d5"], ["col", "4", "d5"], ["row", "2", "d5"]],
      [["color", "pink", "d5"], ["row", "2", "d5"], ["col", "4", "d5"]],
      [["color", "pink", "d5"], ["col", "4", "d5"], [Rel, "below", "d5", "d4"], ["color", "yellow", "d4"]],
      [["color", "pink", "d5"], ["row", "2", "d5"]],
    ],

    6: [
      [["col", "3", "d6"], ["row", "2", "d6"]],
      [["row", "2", "d6"], ["col", "3", "d6"]],
      [["row", "2", "d6"], ["col", "3", "d6"]],
      [["color", "yellow", "d6"], [Rel, "above", "d6", "d11"], ["color", "yellow", "d11"]],
      [["color", "yellow", "d6"], ["row", "2", "d6"]],
      [["color", "yellow", "d6"], ["row", "2", "d6"]],
      [[Rel, "right", "d6", "d7"], [Rel, "right" "d7", "d8"], ["color", "blue", "d7"], ["color", "blue", "d8"]],
      [["color", "yellow", "d6"], [Rel, "above", "d6", "d11"], ["color", "yellow", "d11"]],
      [["color", "yellow", "d6"], ["col", "3", "d6"], ["row", "2", "d6"]],
      [["col", "3", "d6"], ["row", "2", "d6"]],
      [["col", "3", "d6"], ["row", "2", "d6"]],
    ],

    7: [
      [["color", "blue", "d7"], ["col", "2", "d7"], ["row", "2", "d7"]],
      [["color", "blue", "d7"], ["col", "2", "d7"], ["row", "2", "d7"]],
      [["color", "blue", "d7"], [Rel, "below", "d7", "d2"], ["col", "2", "d7"], ["col", "2", "d2"]],
      [["col", "2", "d7"], ["row", "2", "d7"]],
      [["color", "blue", "d7"], [Rel, "below", "d7", "d2"], ["color", "orange", "d2"]],
      [["col", "2", "d7"], ["row", "2", "d7"]],
      [["row", "2", "d7"], ["col", "2", "d7"]],
      [["col", "2", "d7"], ["row", "2", "d7"]],
      [["row", "2", "d7"], ["col", "2", "d7"]],
      [["col", "2", "d7"], ["row", "2", "d7"]],
    ],

    8: [
      [["row", "2", "d8"], ["col", "1", "d8"]],
      [["col", "1", "d8"], ["row", "2", "d8"]],
      [["row", "2", "d8"], ["col", "1", "d8"]],
      [["color", "blue", "d8"], ["row", "2", "d8"], ["col", "1", "d8"]],
      [["row", "2", "d8"], ["col", "1", "d8"]],
      [["row", "2", "d8"], ["col", "1", "d8"]],
      [["row", "2", "d8"], ["col", "1", "d8"]],
    ],

    9: [
      [["color", "orange", "d9"], ["col", "1", "d9"], ["row", "3", "d9"]],
      [["color", "orange", "d9"], ["col", "1", "d9"], ["row", "3", "d9"]],
      [["color", "orange", "d9"], ["col", "1", "d9"], ["row", "3", "d9"]],
      [["row", "3", "d9"], ["col", "1", "d9"]],
      [["color", "orange", "d9"], ["col", "1", "d9"]],
      [["color", "orange", "d9"], ["col", "1", "d9"]],
      [["row", "3", "d9"], ["col", "1", "d9"]],
      [["color", "orange", "d9"], ["col", "1", "d9"]],
    ],

    10: [
      [["color", "blue", "d10"], ["row", "3", "d10"], ["col", "2", "d10"]],
      [["color", "blue", "d10"], ["row", "3", "d10"]],
      [["color", "blue", "d10"], [Rel, "above", "d10", "d15"], ["color", "pink", "d15"]],
      [["color", "blue", "d10"], [Rel, "above", "d10", "d15"], ["color", "pink", "d15"]],
      [["col", "2", "d10"], ["row", "3", "d10"]],
    ],

    11: [
      [["col", "3", "d11"], ["row", "3", "d11"]],
      [["row", "3", "d11"], ["col", "3", "d11"]],
      [["color", "yellow", "d11"], [Rel, "next", "d11", "d12"], ["color", "orange", "d12"]],
      [["color", "yellow", "d11"], [Rel, "next", "d11", "d12"], ["color", "orange", "d12"]],
      [["color", "yellow", "d11"], ["row", "3", "d11"], ["col", "3", "d11"]],
      [["row", "3", "d11"], ["col", "3", "d11"]],
      [["color", "yellow", "d11"], ["row", "3", "d11"]],
      [["color", "yellow", "d11"], ["row", "3", "d11"]],
    ],

    12: [
      [["color", "orange", "d12"], ["col", "4", "d12"]],
      [["row", "3", "d12"], ["col", "4", "d12"]],
      [["color", "orange", "d12"], [Rel, "below", "d12", "d5"], ["color", "pink", "d5"]],
      [["row", "3", "d12"], ["col", "4", "d12"]],
    ],

    13: [
      [["row", "4", "d13"], ["col", "4", "d13"]],
      [["color", "pink", "d13"], ["row", "4", "d13"], ["col", "4", "d13"]],
      [["row", "4", "d13"], ["col", "4", "d13"]],
      [["row", "4", "d13"], ["col", "4", "d13"]],
    ],

    14: [
      [["color", "orange", "d14"], ["row", "4", "d14"], ["col", "3", "d14"]],
      [["color", "orange", "d14"], ["row", "4", "d14"], ["col", "3", "d14"]],
      [["color", "orange", "d14"], ["row", "4", "d14"]],
      [["color", "orange", "d14"], ["row", "4", "d14"]],
      [["color", "orange", "d14"], ["row", "4", "d14"]],
      [["color", "orange", "d14"], [Rel, "below", "d14", "d11"], [Rel, "below", "d11", "d6"], ["color", "yellow", "d11"], ["color", "yellow", "d6"]],
      [["color", "orange", "d14"], ["row", "4", "d14"]],
      [["color", "orange", "d14"], [Rel, "below", "d14", "d11"], [Rel, "below", "d11", "d6"], ["color", "yellow", "d11"], ["color", "yellow", "d6"]],
      [["color", "orange", "d14"], ["row", "4", "d14"]],
    ],

    15: [
      [["col", "2", "d15"], ["row", "4", "d15"]],
      [["color", "pink", "d15"], ["row", "4", "d15"], ["col", "2", "d15"]],
      [["color", "pink", "d15"], ["row", "4", "d15"], ["col", "2", "d15"]],
      [["color", "pink", "d15"], ["col", "2", "d15"]],
      [["color", "pink", "d15"], ["row", "4", "d15"], ["col", "2", "d15"]],
      [["col", "2", "d15"], ["row", "4", "d15"]],
      [["color", "pink", "d15"], ["row", "4", "d15"], ["col", "2", "d15"]],
      [["color", "pink", "d15"], ["row", "4", "d15"], ["col", "2", "d15"]],
      [["color", "pink", "d15"], ["col", "2", "d15"]],
      [["color", "pink", "d15"], ["row", "4", "d15"], ["col", "2", "d15"]],
    ],

    16: [
      [["row", "4", "d16"], ["col", "1", "d16"]],
      [["row", "4", "d16"], ["col", "1", "d16"]],
      [["row", "4", "d16"], ["col", "1", "d16"]],
      [["row", "4", "d16"], ["col", "1", "d16"]],
      [["row", "4", "d16"], ["col", "1", "d16"]],
      [["row", "4", "d16"], ["col", "1", "d16"]],
      [["row", "4", "d16"], ["col", "1", "d16"]],
      [["row", "4", "d16"], ["col", "1", "d16"]],
      [["row", "4", "d16"], ["col", "1", "d16"]],
      [["row", "4", "d16"], ["col", "1", "d16"]],
      [["row", "4", "d16"], ["col", "1", "d16"]],
      [["row", "4", "d16"], ["col", "1", "d16"]],
    ],
  }

  shuffle(facts, lambda: 0.0)

  fb = FullBrevity(filter(lambda f: f[0] != Rel, facts))
  rel = Relational(facts)
  #The ordered priority for using attributes, important for incremental algorithm
  ranked_attrs = ["color", "row", "col", "corner"]
  #Taxonomy used in incremental algorithm to pick out a more common name when appropriate
  # For instance dog instead of Chihuahua when there is a referent dog amongst other animals (which are not dogs)
  taxonomy = Taxonomy({})
  incr = Incremental(facts, ranked_attrs, taxonomy)

  #defines how to turn these rules into English phrases
  handlers = {
    "col": lambda(desc): "column %s" % desc,
    "row": lambda(desc): "row %s" % desc,
    "corner": lambda(desc): "corner",
    "above": lambda(lr): "above" if lr else "below",
    "below": lambda(lr): "below" if lr else "above",
    "right": lambda(lr): "to the right of" if lr else "to the left of",
    "left": lambda(lr): "to the left of" if lr else "to the right of"
  }
  
  #Generate phrases with each algorithm and print to screen
  for i in range(1, 17):
    obj_id = "d%s" % i
    print "%#02d,\"Full Brevity\",\"%s\"" % (i, generate_phrase(fb.describe(obj_id), ranked_attrs, handlers))
    print "%#02d,\"Relational\",\"%s\"" % (i, generate_phrase_rel(rel.describe(obj_id), ranked_attrs, obj_id, handlers))
    print "%#02d,\"Incremental\",\"%s\"" % (i, generate_phrase(incr.describe(obj_id), ranked_attrs, handlers))

