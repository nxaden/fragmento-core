# Domain Layer

## Purpose

The domain layer defines the core meaning of `pytimeslice`. It contains the
concepts, rules, and transformations that determine what a time-slice render is
and how it should behave.

Its job is to represent rendering intent and translate that intent into deterministic image construction rules. This layer should not depend on UI code, file system access, Pillow, OpenCV, or workflow orchestration.

This makes the engine easier to reason about because the most important rendering logic remains isolated from infrastructure and interface concerns.

## What the Domain Layer Is

The domain layer is the part of the system that models the rendering problem itself.

Examples:

* a `TimesliceSpec`
* a `SliceBand`
* a `TimeslicePlan`
* a `CompositeResult`
* validation rules around image dimensions and slice counts
* slice planning and compositing behavior

The domain layer should define what the engine means by a valid render rather than how files are loaded or how a CLI command is invoked.

For example, the domain may:

1. validate a render specification
2. determine how many slices should exist
3. map source frames to slice bands
4. build a time-slice plan
5. compose a final result from that plan

## Responsibilities of the Domain Layer

The domain layer should, for example:

* define the core rendering models
* define rendering rules and invariants
* perform slice planning
* perform compositing
* reject invalid rendering states
* return structured render results

The domain layer should not, for example:

* discover files in folders
* decode JPGs with Pillow or OpenCV
* save outputs to disk
* parse CLI arguments
* coordinate end-to-end workflows

## Why the Domain Layer Matters

Without a clear domain layer, rendering rules tend to leak into infrastructure or interface code. That makes the engine harder to test, harder to extend, and harder to trust.

The domain layer solves that by creating one canonical place for the core business logic. The rest of the system can then depend on those rules without redefining them.

## Example Domain Boundary

A `TimeslicePlan` is a good example of a domain concept.

Its responsibility is not to know where images came from or where results will be saved. Its responsibility is to describe how a final composite should be assembled.

Typical inputs:

* normalized images
* `TimesliceSpec`

Typical outputs:

* `TimeslicePlan`
* `CompositeResult`
* used frame indices
* validated rendering state

## Relationship to Other Layers

The domain layer should be independent from the other layers.

A typical flow looks like this:

Interface → Application Service → Domain + Infrastructure → Result

For example:

* infrastructure loads images
* application layer coordinates the workflow
* domain validates the render specification
* domain builds the plan and composite
* application returns the result
* interface presents the output

## Extensibility

The domain layer is a good extensibility point because it lets you add new rendering behavior without rewriting interfaces or infrastructure.

For example, we can extend `pytimeslice` with alternate frame selection
strategies, richer plans, alignment-aware planning, or metadata-rich render
results.

Each new domain concept can build on the same rendering models and rules while extending the meaning of the engine in a controlled way.
