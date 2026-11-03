"""Single source of truth for every value drawn on the blueprint sheets.

Each dimension records its value, the forum post(s) it comes from, and a status:

  sourced    stated in the post
  derived    calculated from sourced values (the calculation is given)
  schematic  shape or position not documented; drawn only to show arrangement

make_drawings.py reads this file to draw the sheets and to write
docs/RENDERINGS.md, which links each sheet and dimension back to the posts and to
the forum photos that show the same part. Photos are linked, never copied.
"""

THREAD = "https://forum.gbfans.com/t/hasbro-1984-proton-pack-big-overhaul-and-customisation/219236"

AUTHORS = {
    4: "gbrich", 6: "gbrich", 12: "gbrich", 15: "gbrich", 16: "gbrich", 20: "gbrich",
    22: "gbrich", 23: "gbrich", 27: "nomake-wan", 29: "gbrich", 30: "nomake-wan",
    32: "gbrich", 49: "gbrich", 54: "spooky", 68: "gbrich", 73: "gbrich", 79: "gbrich",
    81: "mcspain", 82: "gbrich", 85: "gbrich", 21: "spooky", 88: "gbrich", 91: "gbrich",
}

D = "https://discdn.gbfans.com/original/3X/"

# Forum photos, by post: (url, what it shows, sheet it shows a part of; "" = none).
PHOTOS = {
    4: [
        (D + "8/f/8fc27369cfcc90504a5cfdd6c2bdfe78d027866c.jpeg", "IMG_5063: stock rubber fittings and hoses, before", "S7"),
        (D + "5/b/5b83ace437106b0bf5f9232822a408251ccc7f42.jpeg", "IMG_5067: brass elbows and Legris fittings installed", "S7"),
    ],
    12: [
        (D + "1/7/177493a655670df5f8cb4a0ef838caba481b5f3b.jpeg", "IMG_5097: metal BNC connectors", "S4"),
        (D + "5/a/5a8fd3c29df521ee6927cb05cd342840f6c136a1.jpeg", "IMG_5098: BNC connectors pushed into the drilled cable stubs", "S4"),
        (D + "c/a/ca5f53d1c26ba9618ad24c283d3ee4dedf2f87ec.jpeg", "IMG_5104: emitter tubes cracked by prying", "S1"),
    ],
    15: [],
    16: [
        (D + "4/7/473c0ce644fc7f35f4a4657bf1b3c7099fac2be2.jpeg", "IMG_5107: trimmed posts that held the emitter LED boards", ""),
        (D + "d/6/d6fafc766834a0720df7435011d5724d38022bc3.jpeg", "IMG_5108: removed LED board and its three post holes", ""),
    ],
    20: [
        (D + "0/a/0a5dcbd15933941334e15af68c34ff1ca8251527.jpeg", "IMG_5129: real M6 bolts in place of the molded HGA bolts", "S7"),
    ],
    23: [
        (D + "a/6/a685fa2601e29dd71ae8d87691c20b7ee9f270ab.jpeg", "IMG_5113: original clear tubes after removal (sacrificed)", "S1"),
        (D + "9/8/987eadaba7a3e18b9bd5233cc9ff8ceace7e2e4f.jpeg", "IMG_5116: caps and inserts masked for paint", "S1"),
        (D + "5/e/5e1276b442c2c3ba781998c24cc35fbf13eb1a25.jpeg", "IMG_5127: caps and inserts after spraying", "S1"),
    ],
    27: [
        (D + "b/b/bbc7d8c9da39f560af913a5786c007cea7b65b57.jpeg", "IMG_0972s: where the blade goes between the HGA and bracket (arrowed)", "S6"),
        (D + "5/8/58513ec02c252dcf3d23b0b5deabb909facd3e60.jpeg", "IMG_1808: HGA rotated and coming out", "S6"),
    ],
    32: [
        (D + "7/2/729ccfe473d384e65d1785ca870994459b4164c8.jpeg", "IMG_5552: finished emitter tubes cut to 23 mm", "S1"),
        (D + "0/d/0d1639238d2563a52913959e65ce7c166ac67d7e.jpeg", "IMG_5555: tubes being glued into the cyclotron lid", "S1"),
        (D + "4/8/48f0980617dd33628e7db98215becc16423ce67a.jpeg", "cyclotron-lid: before and after", "S1"),
    ],
    49: [
        (D + "9/5/955d55b31f88b0e8ebce6a3804ec905114ea24f4.jpeg", "IMG_5685: frosted acrylic cake window on M2.5 screws", "S7"),
    ],
    68: [
        (D + "1/3/1386653b8604aa6fdcf65499419dfec7f81f2a3a.jpeg", "IMG_5703: speaker holes relative to the DANGER sticker", "S7"),
        (D + "3/6/361f31f99d4b7067fb7a3135c8ce4f69a973f8c2.jpeg", "IMG_5725: mesh glued behind the speaker holes", "S7"),
        (D + "8/6/8617a022450044dc238221d11ee245b257f3959d.jpeg", "IMG_5734: ALICE mounting bolt protruding through the board", "S2"),
        (D + "b/a/ba92cbbc5e0e4d14edab1fcc1b80729ec17e01ea.jpeg", "IMG_5757: printed spacer in place under the washer", "S2"),
    ],
    73: [
        (D + "3/e/3ed46f523d34103e564da3cbc1c615cc99cb9ece.jpeg", "IMG_5767: M3 bolts and nuts replacing the rivets", "S7"),
        (D + "4/7/4735d371baf5abf1bd6882ee55603f619d47dac8.jpeg", "IMG_5765: C&A ribbon cable clamp on its new 3 mm holes", "S7"),
        (D + "9/4/946186e7698ba5ca50e5a9d541917266f9010966.jpeg", "IMG_5761: finished ALICE frame neck foam", "S3"),
        (D + "5/e/5eb3520831722e37c72fff487e17e01b0c75e60c.jpeg", "Neck Foam: gbrich's measurement template", "S3"),
        (D + "3/0/30cef3101bbc421dd1a318e08f440654ca61d870.jpeg", "IMG_5764: ion arm end cap secured with M3 bolts", "S5"),
    ],
    81: [
        (D + "6/3/635182272e7ce0eec857922744280b0c543de253.jpeg", "Removed HGA (mcspain; bracket cut away)", "S6"),
        (D + "7/8/7855f2a0fe5b7fdfa2f5d451331277bc1832f3fb.jpeg", "EmitterTubesLid: mcspain's rebuilt emitter tubes", "S1"),
    ],
}

# Every drawn value. key: (value, unit, posts, status, note)
DIMS = {
    # Emitter tubes
    "tube_od": (14, "mm", [23], "sourced", "Clear acrylic tube outside diameter"),
    "tube_id": (12, "mm", [23], "sourced", "Inside diameter"),
    "tube_len": (23, "mm", [32], "sourced", "Cut length"),
    "insert_len": (22, "mm", [23, 32], "sourced", "Black insert length, excluding its nub"),
    "tube_play": (1, "mm", [32], "derived", "23 mm tube - 22 mm insert"),
    "tube_stock": (305, "mm", [23], "sourced", "Length of tube bought"),
    "tube_reject_id": (11, "mm", [12, 23], "sourced", "ID that was too small for the inserts"),
    "tube_reject_od": (15, "mm", [23], "sourced", "OD that did not fit the lid housing"),
    "saw_blade": (60, "teeth", [32], "sourced", "Fine-cut mitre saw blade that gave square cuts"),

    # ALICE frame spacer
    "sp_od": (20, "mm", [68], "sourced", "Printed spacer outside diameter"),
    "sp_id": (8, "mm", [68], "sourced", "Inside diameter"),
    "sp_t": (3, "mm", [68], "sourced", "Thickness"),
    "bolt_over": (3, "mm", [68], "sourced", "How far the kit bolts were too long (approximate, 'about 3mm')"),

    # Neck pad
    "np_id": (22, "mm", [73], "sourced", "Pipe insulation inside diameter"),
    "np_wall": (13, "mm", [73], "sourced", "Insulation wall thickness"),
    "np_od": (48, "mm", [73], "sourced", "Insulation outside diameter (22 + 2 x 13)"),
    "np_skin": (3, "mm", [73], "sourced", "Adhesive neoprene/foam sheet"),
    "np_od_total": (54, "mm", [73], "derived", "48 + 2 x 3 mm covering"),
    "np_circ": (160.2, "mm", [73], "derived", "Covering width to wrap the insulation: pi x (48 + 3) mm, measured at the sheet's mid-thickness"),

    # BNC cable ends
    "bnc_bore": (5.5, "mm", [12], "sourced", "Drill into cable stub for a friction fit, no glue"),
    "bnc_bore_alt": (6, "mm", [12], "sourced", "Alternative drill; needs glue"),

    # Ion arm end cap
    "ia_hole": (3, "mm", [73], "sourced", "Two holes through the centers of the molded fake bolts"),
    "ia_bolt_len": (20, "mm", [73], "sourced", "M3 x 20 mm bolts"),

    # HGA
    "hga_rot": (30, "deg", [27], "sourced", "Rotation to align the HGA tabs with the crank generator slots"),
    "hga_screws": (2, "pcs", [27], "sourced", "Bracket screws"),

    # Drill and hardware chart
    "legris_hole": (9, "mm", [4], "sourced", "Approximate hole for brass elbow/Legris ('I think you need 9mm'), widened from an 8 mm bit"),
    "speaker_holes": (5, "mm", [68], "sourced", "Seven holes in the aluminum motherboard over the GPStar speaker"),
    "clamp_holes": (3, "mm", [73], "sourced", "Two holes just right of the stock clamp holes, for the C&A clamp"),
    "banjo_hole": (4.5, "mm", [79], "sourced", "Wand wing hole widened with a 4 or 4.5 mm bit for the Mack's banjo screw"),
    "toggle_holes": (6.5, "mm", [85], "sourced", "Two holes for dummy toggle switches in the cyclotron"),
    "bolt_m6": (6, "mm", [20, 22, 30], "sourced", "Black M6 bolts and washers replacing molded HGA bolts; originals were 1/4-20"),
    "redman_shell": (7.94, "mm", [68], "sourced", "5/16 in, the hole size in Redman's instructions for the structural shell bolts"),
    "cake_screw": (2.5, "mm", [49, 68], "sourced", "M2.5 black button-head screws for the cake lid window"),
    "rivet_bolt": (3, "mm", [73], "sourced", "Short M3 button-head bolts and nuts replacing the rivets"),
    "stand_ext": (75, "mm", [85], "sourced", "Extension added to each of two stand parts for a spacer-mounted ALICE frame"),
}

# Sheets: id, file stem, title, posts whose photos show the part, dims used
SHEETS = [
    ("S1", "s1_emitter_tubes", "CRT emitter tube rebuild", [12, 23, 32, 81],
     ["tube_od", "tube_id", "tube_len", "insert_len", "tube_play", "tube_reject_id", "tube_reject_od", "tube_stock", "saw_blade"]),
    ("S2", "s2_alice_spacer", "ALICE frame mounting spacer", [68],
     ["sp_od", "sp_id", "sp_t", "bolt_over"]),
    ("S3", "s3_neck_pad", "ALICE frame neck pad", [73],
     ["np_id", "np_wall", "np_od", "np_skin", "np_od_total", "np_circ"]),
    ("S4", "s4_bnc_ends", "BNC cable ends", [12],
     ["bnc_bore", "bnc_bore_alt"]),
    ("S5", "s5_ion_arm_cap", "Ion arm end cap pinning", [73],
     ["ia_hole", "ia_bolt_len"]),
    ("S6", "s6_hga_removal", "HGA removal (non-destructive)", [27, 81],
     ["hga_screws", "hga_rot"]),
    ("S7", "s7_drill_chart", "Drill and hardware chart (print at 100%)", [4, 20, 49, 68, 73],
     ["legris_hole", "bnc_bore", "bnc_bore_alt", "speaker_holes", "clamp_holes", "ia_hole", "banjo_hole",
      "toggle_holes", "bolt_m6", "redman_shell", "cake_screw", "rivet_bolt"]),
]


def post_url(n: int) -> str:
    return f"{THREAD}/{n}"
