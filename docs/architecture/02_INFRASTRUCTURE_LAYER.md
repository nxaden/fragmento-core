# Infrastructure Layer

## Purpose

The infrastructure layer handles the technical details that allow
`pytimeslice` to interact with the outside world. It provides the concrete
adapters that support rendering without defining the rendering rules
themselves.

Its job is to manage concerns such as file discovery, image decoding, resizing or cropping, integration with Pillow or OpenCV, caching, and output writing. Each of the previous concerns listed would typically be represented by one or more concrete adapters in the infrastructure layer. This layer should not contain slice planning rules, compositing policy, or UI-specific behavior.

This makes the app easier to extend because the core engine can remain stable while different technical implementations are swapped in or improved over time.

## What the Infrastructure Layer Is

The infrastructure layer is the part of the system that implements external or technical capabilities.

Examples:

* discovering image paths in a folder
* loading images into RGB arrays
* resizing or cropping images to a common size
* saving rendered outputs to disk
* exporting metadata files
* integrating with Pillow, OpenCV, or future storage backends

An infrastructure adapter should implement a technical capability rather than redefine the meaning of a render.

For example, an image loader may:

1. scan a folder for supported image files
2. sort the discovered paths
3. decode the files into RGB arrays
4. normalize dimensions through resize or crop behavior
5. return the loaded images to the application layer

## Responsibilities of the Infrastructure Layer

The infrastructure layer should, for example:

* implement file and image I/O
* provide loaders and writers
* integrate external libraries such as Pillow or OpenCV
* normalize source images into a usable representation
* persist outputs to disk or other storage
* surface technical errors from those operations

The infrastructure layer should not, for example:

* define what a valid time-slice means
* perform slice planning
* define compositing rules
* parse CLI arguments
* coordinate full application workflows

## Why the Infrastructure Layer Matters

Without a clear infrastructure layer, technical details tend to leak into the domain or interface code. That makes the engine harder to test, harder to replace, and harder to evolve when dependencies change.

The infrastructure layer solves that by creating one canonical place for technical adapters. The rest of the system can then depend on those capabilities without being tightly coupled to specific libraries or file formats.

## Example Infrastructure Boundary

A `PILImageSequenceLoader` is a good example of an infrastructure adapter.

Its responsibility is not to know how a time-slice is planned. Its responsibility is to discover and decode source images into a normalized in-memory form that the rest of the engine can use.

Typical inputs:

* source folder
* image paths
* resize mode

Typical outputs:

* ordered image paths
* normalized RGB images
* file and decoding errors when loading fails

## Relationship to Other Layers

The infrastructure layer supports the application and domain layers without defining their meaning.

A typical flow looks like this:

Interface → Application Service → Domain + Infrastructure → Result

For example:

* application requests source images
* infrastructure discovers and loads the files
* domain builds the plan and composite
* infrastructure may save the output
* application returns the result
* interface presents the outcome

## Extensibility

The infrastructure layer is a good extensibility point because it lets you change technical implementations without changing the core rendering logic.

For example, we can extend `pytimeslice` with alternative loaders,
OpenCV-based preprocessing, metadata writers, cache backends, or cloud storage
adapters.

Each new adapter can reuse the same application workflows and domain models while changing only how the system interacts with external tools and resources.
