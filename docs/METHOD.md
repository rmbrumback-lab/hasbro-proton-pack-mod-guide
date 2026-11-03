# Measurement method

How dimensions of the Hasbro 1984 Proton Pack are inferred from photographs, and how each value is validated. Nobody has published dimensions for the pack, so every blueprint value is either **measured** by a person with a tool, or **estimated** from photos using the method below. The two are never mixed: estimates are always drawn as estimates.

## Sources

| Code | Source | Use |
|---|---|---|
| **H** | Hasbro Pulse product photos of the 1984 pack (G19145L00) | proportions and layout; no scale reference in frame |
| **F** | Photos in the GBFans overhaul thread | scale, because many show parts of known size in the same plane |
| **M** | HasLab Spengler's Proton Pack manual (F5226), Hasbro | part names, assembly order, shared tooling |
| **T** | Measurements stated in the thread (for example the 14 mm emitter tube) | scale references and direct values |

Third-party photos are downloaded to a local working cache only, for measurement. They are not redistributed in this repository; the attribution links to them.

## Scale references

A photo can only be measured once something in it has a known size. References are ranked:

1. **Measured in the thread (T):** values a builder measured with a tool, such as the 14 mm OD / 12 mm ID emitter tube (post #23), the 22 mm insert (post #32), the 6 mm red and blue hoses (post #4).
2. **Standard hardware:** parts made to a published size, such as M6 and M3 bolts and washers (ISO 7089 washer OD: M6 = 12 mm, M3 = 7 mm), BNC connectors, Legris fittings, 20 AWG silicone wire (1.8 mm OD as sold, post #32).
3. **Derived from the pack:** a pack dimension already established by two independent references above can then serve as a reference itself. Its uncertainty carries forward.

## Measuring a photo

1. **Pick features in one plane.** Only measure a feature that lies in the same plane as its reference, and roughly square to the camera. Anything else is either corrected or not measured.
2. **Correct perspective** where four or more points on a known flat rectangle are visible (homography). Record the correction.
3. **Measure in pixels** at full resolution, at both edges of each feature, and record the pixel coordinates so the measurement can be repeated.
4. **Convert** with the reference: `size = pixels × (reference size / reference pixels)`.
5. **Estimate the error** from: edge sharpness (± pixels at each edge), the reference's own tolerance, depth difference between feature and reference, and residual perspective.

## Validation

A value becomes an estimate on a blueprint only when:

- it has been measured in **at least two different photos**, and
- against **at least two independent references** (not the same reference measured twice), and
- the results agree within their combined uncertainty.

The value drawn is the weighted mean, with a ± range that covers all the measurements. If measurements disagree, the value is **flagged** in the register and not drawn until resolved. Every value has a register entry listing each measurement: photo, pixel coordinates, reference used and result.

## Status on the drawings

| Status | Meaning | Drawn as |
|---|---|---|
| **measured** | stated by a person who measured it with a tool | white, post number |
| **estimated** | inferred from photos by this method, validated as above | amber, with ± range and register ID |
| **derived** | calculated from other values | light blue italics, with the calculation |
| **schematic** | layout only, not measured | dashed, stamped *schematic* |

Expected accuracy for photo estimates (an estimate, not a guarantee): about ±2–5% for flat features measured against a reference in the same plane; worse for curved surfaces, edges seen at an angle, or features far from the reference. Each value carries its own range, so the drawings never imply caliper precision.
