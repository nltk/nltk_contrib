from full_brevity import *
from incremental import *
from relational import *

import util

def getFacts():
    """
    Always numbered from left to right
    Referent is alwasy r1
    Distractors are labeled based on the first letter of their type
    s1 = first sphere, c1= first cube, s2 = second sphere etc.
    This data was entered manually, but came from analyzing the
    the pictures from the GRE3D data set provided by Viethen and Dale 2008.
    """
    facts = {}
    facts[1] =  [[Type, "sphere", "r1"], [Type, "cube", "c1"], [Type, "cube", "c2"],
                 ["color", "green", "r1"], ["color", "blue", "c1"], ["color", "blue", "c2"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "c1"],["size", "large", "c2"],
                 [Rel, "left_of", "c1", "c2"], [Rel, "right_of", "c2", "c1"],
                 [Rel, "left_of", "c1", "r1"], [Rel, "right_of", "r1", "c1"],
                 ["side", "right", "r1"], ["side", "left", "c1" ], ["side", "right", "c2" ],
                 [Rel, "on", "r1", "c2"], [Rel, "on", "c2", "f1"], [Rel, "on", "c1", "f1"],
                 [Rel, "under", "f1", "c2"], [Rel, "under", "f1", "c1"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                 ]
                

    facts[2] =  [[Type, "sphere", "r1"], [Type, "cube", "c1"], [Type, "cube", "c2"],
                 ["color", "red", "r1"], ["color", "yellow", "c1"], ["color", "red", "c2"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "c1"],["size", "small", "c2"],
                 [Rel, "left_of", "c1", "c2"], [Rel, "right_of", "c2", "c1"],
                 [Rel, "left_of", "r1", "c2"], [Rel, "right_of", "c2", "r1"],
                 ["side", "left", "r1"], ["side", "left", "c1" ], ["side", "right", "c2" ],
                 [Rel, "in_front_of", "r1", "c1"], [Rel, "behind", "c1", "r1"],
                 [Rel, "on", "r1", "f1"], [Rel, "on", "c1", "f1"], [Rel, "on", "c2", "f1"],
                 [Rel, "under", "f1", "r1"], [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "c2"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[3] =  [[Type, "sphere", "r1"], [Type, "sphere", "s1"], [Type, "cube", "c1"],
                 ["color", "blue", "r1"], ["color", "blue", "s1"], ["color", "green", "c1"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "s1"],["size", "large", "c1"],
                 [Rel, "left_of", "s1", "c1"], [Rel, "right_of", "c1", "s1"],
                 [Rel, "left_of", "s1", "r1"], [Rel, "right_of", "r1", "s1"],
                 ["side", "right", "r1"], ["side", "left", "s1" ], ["side", "right", "c1" ],
                 [Rel, "on", "r1", "c1"], [Rel, "under", "c1", "r1"], 
                 [Rel, "on", "c1", "f1"], [Rel, "on", "s1", "f1"], 
                 [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "s1"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[4] =  [[Type, "cube", "r1"], [Type, "cube", "c1"], [Type, "cube", "c2"],
                 ["color", "yellow", "r1"], ["color", "yellow", "c1"], ["color", "red", "c2"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "c1"],["size", "small", "c2"],
                 [Rel, "left_of", "c1", "c2"], [Rel, "right_of", "c2", "c1"],
                 [Rel, "left_of", "r1", "c2"], [Rel, "right_of", "c2", "r1"],
                 ["side", "left", "r1"], ["side", "left", "c1" ], ["side", "right", "c2" ],
                 [Rel, "in_front_of", "r1", "c1"], [Rel, "behind", "c1", "r1"],
                 [Rel, "on", "r1", "f1"], [Rel, "on", "c1", "f1"], [Rel, "on", "c2", "f1"],
                 [Rel, "under", "f1", "r1"], [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "c2"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[5] =  [[Type, "cube", "r1"], [Type, "sphere", "s1"], [Type, "cube", "c1"],
                 ["color", "blue", "r1"], ["color", "blue", "s1"], ["color", "green", "c1"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "s1"],["size", "small", "c1"],
                 [Rel, "left_of", "s1", "c1"], [Rel, "right_of", "c1", "s1"],
                 [Rel, "left_of", "s1", "r1"], [Rel, "right_of", "r1", "s1"],
                 ["side", "right", "r1"], ["side", "left", "s1" ], ["side", "right", "c1" ],
                 [Rel, "on", "r1", "c1"], [Rel, "under", "c1", "r1"],
                 [Rel, "on", "s1", "f1"], [Rel, "on", "c1", "f1"],
                 [Rel, "under", "f1", "s1"], [Rel, "under", "f1", "c1"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[6] =  [[Type, "sphere", "r1"], [Type, "cube", "c1"], [Type, "cube", "c2"],
                 ["color", "green", "r1"], ["color", "blue", "c1"], ["color", "blue", "c2"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "c1"],["size", "large", "c2"],
                 [Rel, "left_of", "c1", "c2"], [Rel, "right_of", "c2", "c1"],
                 [Rel, "left_of", "r1", "c2"], [Rel, "right_of", "r1", "c1"],
                 ["side", "left", "r1"], ["side", "left", "c1" ], ["side", "right", "c2" ],
                 [Rel, "in_front_of", "r1", "c1"], [Rel, "behind", "c1", "r1"],
                 [Rel, "on", "r1", "f1"],[Rel, "on", "c1", "f1"], [Rel, "on", "c2", "f1"],
                 [Rel, "under", "f1", "r1"],[Rel, "under", "f1", "c1"], [Rel, "under", "f1", "c2"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[7] =  [[Type, "sphere", "r1"], [Type, "cube", "c1"], [Type, "cube", "c2"],
                 ["color", "yellow", "r1"], ["color", "yellow", "c1"], ["color", "red", "c2"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "small", "c1"],["size", "large", "c2"],
                 [Rel, "left_of", "c1", "c2"], [Rel, "right_of", "c2", "c1"],
                 [Rel, "left_of", "c1", "r1"], [Rel, "right_of", "r1", "c1"],
                 ["side", "right", "r1"], ["side", "left", "c1" ], ["side", "right", "c2" ],
                 [Rel, "on", "r1", "c2"], [Rel, "under", "c2", "r1"], 
                 [Rel, "on", "c1", "f1"], [Rel, "on", "c2", "f1"],
                 [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "c2"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[8] =  [[Type, "sphere", "r1"], [Type, "cube", "c1"], [Type, "sphere", "s1"],
                 ["color", "blue", "r1"], ["color", "green", "c1"], ["color", "blue", "s1"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "c1"],["size", "large", "s1"],
                 [Rel, "left_of", "c1", "s1"], [Rel, "right_of", "s1", "c1"],
                 [Rel, "left_of", "r1", "s1"], [Rel, "right_of", "s1", "r1"],
                 ["side", "left", "r1"], ["side", "left", "c1" ], ["side", "right", "s1" ],
                 [Rel, "in_front_of", "r1", "c1"], [Rel, "behind", "c1", "r1"], 
                 [Rel, "on", "r1", "f1"], [Rel, "on", "c1", "f1"], [Rel, "on", "s1", "f1"],
                 [Rel, "under", "f1", "r1"], [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "s1"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]


    facts[9] =  [[Type, "cube", "r1"], [Type, "cube", "c1"], [Type, "cube", "c2"],
                 ["color", "red", "r1"], ["color", "yellow", "c1"], ["color", "red", "c2"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "small", "c1"],["size", "large", "c2"],
                 [Rel, "left_of", "c1", "c2"], [Rel, "right_of", "c2", "c1"],
                 [Rel, "left_of", "c1", "r1"], [Rel, "right_of", "r1", "c1"],
                 ["side", "right", "r1"], ["side", "left", "c1" ], ["side", "right", "c2" ],
                 [Rel, "on", "r1", "c2"], [Rel, "under", "c2", "r1"], 
                 [Rel, "on", "c1", "f1"], [Rel, "on", "c2", "f1"],
                 [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "c2"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[10] =  [[Type, "cube", "r1"], [Type, "cube", "c1"], [Type, "sphere", "s1"],
                 ["color", "blue", "r1"], ["color", "green", "c1"], ["color", "blue", "s1"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "small", "c1"],["size", "large", "s1"],
                 [Rel, "left_of", "c1", "s1"], [Rel, "right_of", "s1", "c1"],
                 [Rel, "left_of", "r1", "s1"], [Rel, "right_of", "s1", "r1"],
                 ["side", "left", "r1"], ["side", "left", "c1" ], ["side", "right", "s1" ],
                 [Rel, "in_front_of", "r1", "c1"], [Rel, "behind", "c1", "r1"],
                 [Rel, "on", "r1", "f1"], [Rel, "on", "c1", "f1"], [Rel, "on", "s1", "f1"],
                 [Rel, "under", "f1", "r1"], [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "s1"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[11] =  [[Type, "sphere", "r1"], [Type, "cube", "c1"], [Type, "cube", "c2"],
                 ["color", "yellow", "r1"], ["color", "red", "c1"], ["color", "red", "c2"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "c1"],["size", "large", "c2"],
                 [Rel, "left_of", "c1", "c2"], [Rel, "right_of", "c2", "c1"],
                 [Rel, "left_of", "r1", "c2"], [Rel, "right_of", "c2", "r1"],
                 ["side", "left", "r1"], ["side", "left", "c1" ], ["side", "right", "c2" ],
                 [Rel, "on", "r1", "c1"], [Rel, "on", "c2", "f1"], [Rel, "on", "c1", "f1"],
                 [Rel, "under", "c1", "r1"], [Rel, "under", "f1", "c2"], [Rel, "under", "f1", "c1"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                 ]
                

    facts[12] =  [[Type, "sphere", "r1"], [Type, "cube", "c1"], [Type, "cube", "c2"],
                 ["color", "blue", "r1"], ["color", "blue", "c1"], ["color", "green", "c2"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "small", "c1"],["size", "large", "c2"],
                 [Rel, "left_of", "c1", "c2"], [Rel, "right_of", "c2", "c1"],
                 [Rel, "left_of", "c1", "r1"], [Rel, "right_of", "r1", "c1"],
                 ["side", "right", "r1"], ["side", "left", "c1" ], ["side", "right", "c2" ],
                 [Rel, "in_front_of", "r1", "c2"], [Rel, "behind", "c2", "r1"],
                 [Rel, "on", "r1", "f1"], [Rel, "on", "c1", "f1"], [Rel, "on", "c2", "f1"],
                 [Rel, "under", "f1", "r1"], [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "c2"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[13] =  [[Type, "sphere", "r1"], [Type, "cube", "c1"], [Type, "sphere", "s1"],
                 ["color", "red", "r1"], ["color", "yellow", "c1"], ["color", "red", "s1"],
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "c1"],["size", "large", "s1"],
                 [Rel, "left_of", "c1", "s1"], [Rel, "right_of", "s1", "c1"],
                 [Rel, "left_of", "r1", "s1"], [Rel, "right_of", "s1", "r1"],
                 ["side", "left", "r1"], ["side", "left", "c1" ], ["side", "right", "s1" ],
                 [Rel, "on", "r1", "c1"], [Rel, "under", "c1", "r1"], 
                 [Rel, "on", "c1", "f1"], [Rel, "on", "s1", "f1"], 
                 [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "s1"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[14] =  [[Type, "cube", "r1"], [Type, "cube", "c1"], [Type, "cube", "c2"],
                 ["color", "green", "r1"], ["color", "blue", "c1"], ["color", "green", "c2"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "c2"],["size", "small", "c1"],
                 [Rel, "left_of", "c1", "c2"], [Rel, "right_of", "c2", "c1"],
                 [Rel, "left_of", "c1", "r1"], [Rel, "right_of", "r1", "c2"],
                 ["side", "left", "r1"], ["side", "left", "c1" ], ["side", "right", "c2" ],
                 [Rel, "in_front_of", "r1", "c2"], [Rel, "behind", "c2", "r1"],
                 [Rel, "on", "r1", "f1"], [Rel, "on", "c1", "f1"], [Rel, "on", "c2", "f1"],
                 [Rel, "under", "f1", "r1"], [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "c2"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[15] =  [[Type, "cube", "r1"], [Type, "cube", "c1"], [Type, "sphere", "s1"],
                 ["color", "yellow", "r1"], ["color", "red", "c1"], ["color", "yellow", "s1"],
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "small", "c1"], ["size", "large", "s1"],
                 [Rel, "right_of", "s1", "c1"], [Rel, "left_of", "c1", "s1"],
                 [Rel, "right_of", "s1", "r1"], [Rel, "left_of", "r1", "s1"],
                 ["side", "left", "r1"], ["side", "right", "s1" ], ["side", "left", "c1" ],
                 [Rel, "on", "r1", "c1"], [Rel, "under", "c1", "r1"],
                 [Rel, "on", "s1", "f1"], [Rel, "on", "c1", "f1"],
                 [Rel, "under", "f1", "s1"], [Rel, "under", "f1", "c1"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[16] =  [[Type, "sphere", "r1"], [Type, "cube", "c1"], [Type, "cube", "c2"],
                 ["color", "red", "r1"], ["color", "yellow", "c1"], ["color", "yellow", "c2"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "c1"],["size", "large", "c2"],
                 [Rel, "left_of", "c1", "c2"], [Rel, "right_of", "c2", "c1"],
                 [Rel, "right_of", "r1", "c1"], [Rel, "left_of", "c1", "r1"],
                 ["side", "right", "r1"], ["side", "left", "c1" ], ["side", "right", "c2" ],
                 [Rel, "in_front_of", "r1", "c2"], [Rel, "behind", "c2", "r1"],
                 [Rel, "on", "r1", "f1"],[Rel, "on", "c1", "f1"], [Rel, "on", "c2", "f1"],
                 [Rel, "under", "f1", "r1"],[Rel, "under", "f1", "c1"], [Rel, "under", "f1", "c2"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[17] =  [[Type, "sphere", "r1"], [Type, "cube", "c1"], [Type, "cube", "c2"],
                 ["color", "blue", "r1"], ["color", "green", "c1"], ["color", "blue", "c2"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "c1"],["size", "small", "c2"],
                 [Rel, "left_of", "c1", "c2"], [Rel, "right_of", "c2", "c1"],
                 [Rel, "left_of", "r1", "c2"], [Rel, "right_of", "c2", "r1"],
                 ["side", "left", "r1"], ["side", "left", "c1" ], ["side", "right", "c2" ],
                 [Rel, "on", "r1", "c1"], [Rel, "under", "c1", "r1"], 
                 [Rel, "on", "c1", "f1"], [Rel, "on", "c2", "f1"],
                 [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "c2"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[18] =  [[Type, "sphere", "r1"], [Type, "sphere", "s1"], [Type, "cube", "c1"],
                 ["color", "red", "r1"], ["color", "red", "s1"], ["color", "yellow", "c1"],
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "s1"],["size", "large", "c1"],
                 [Rel, "right_of", "c1", "s1"], [Rel, "left_of", "s1", "c1"],
                 [Rel, "right_of", "r1", "s1"], [Rel, "left_of", "s1", "r1"],
                 ["side", "right", "r1"], ["side", "left", "c1" ], ["side", "right", "s1" ],
                 [Rel, "in_front_of", "r1", "c1"], [Rel, "behind", "c1", "r1"], 
                 [Rel, "on", "r1", "f1"], [Rel, "on", "c1", "f1"], [Rel, "on", "s1", "f1"],
                 [Rel, "under", "f1", "r1"], [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "s1"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]


    facts[19] =  [[Type, "cube", "r1"], [Type, "cube", "c1"], [Type, "cube", "c2"],
                 ["color", "green", "r1"], ["color", "green", "c1"], ["color", "blue", "c2"], 
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "large", "c1"],["size", "small", "c2"],
                 [Rel, "left_of", "c1", "c2"], [Rel, "right_of", "c2", "c1"],
                 [Rel, "left_of", "r1", "c2"], [Rel, "right_of", "c2", "r1"],
                 ["side", "left", "r1"], ["side", "left", "c1" ], ["side", "right", "c2" ],
                 [Rel, "on", "r1", "c1"], [Rel, "under", "c1", "r1"], 
                 [Rel, "on", "c1", "f1"], [Rel, "on", "c2", "f1"],
                 [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "c2"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    facts[20] =  [[Type, "cube", "r1"], [Type, "sphere", "s1"], [Type, "cube", "c1"],
                 ["color", "red", "r1"], ["color", "red", "s1"], ["color", "yellow", "c1"],
                 [Type, "floor", "f1"],
                 ["size", "small", "r1"], ["size", "small", "c1"],["size", "large", "s1"],
                 [Rel, "left_of", "s1", "c1"], [Rel, "right_of", "c1", "s1"],
                 [Rel, "left_of", "s1", "r1"], [Rel, "right_of", "r1", "s1"],
                 ["side", "right", "r1"], ["side", "left", "s1" ], ["side", "right", "c1" ],
                 [Rel, "in_front_of", "r1", "c1"], [Rel, "behind", "c1", "r1"],
                 [Rel, "on", "r1", "f1"], [Rel, "on", "c1", "f1"], [Rel, "on", "s1", "f1"],
                 [Rel, "under", "f1", "r1"], [Rel, "under", "f1", "c1"], [Rel, "under", "f1", "s1"],
                 ["color", "None", "f1"], ["size", "None", "f1"], ["side", "None", "f1"]
                ]

    return facts

if __name__ == '__main__':
  facts = getFacts()

  ranked_attrs = ["color", "size", Type]
  taxonomy = Taxonomy({})

  handlers = {
    "in_front_of": lambda(lr): "in front of",
    "left_of": lambda(lr): "to the left of",
    "right_of": lambda(lr): "to the right of"
  }

  #Print out the referring expressions generated by each algorithm for each scene
  for i in range(1, 21):
    fb = FullBrevity(facts[i])
    desc_fb = fb.describe("r1")

    incr = Incremental(facts[i], ranked_attrs, taxonomy)
    desc_incr = incr.describe("r1")

    rel = Relational(facts[i])
    desc_rel = rel.describe("r1")

    print "%#02d,\"Full Brevity\",\"%s\"" % (i, util.generate_phrase(desc_fb, ranked_attrs))
    print "%#02d,\"Incremental\",\"%s\"" % (i, util.generate_phrase(desc_incr, ranked_attrs))
    print "%#02d,\"Relational\",\"%s\"" % (i, util.generate_phrase_rel(desc_rel, ranked_attrs, "r1", handlers))

