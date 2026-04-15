# Application Layer

## Purpose

The application layer exists to orchestrate use cases. It sits between the interface layer and the domain layer.

Its job is to coordinate workflows such as rendering a timeslice from a folder, generating a preview, exporting a result, or loading a saved project. Each of the previous use cases listed would constitute a new 'service' in the application layer. This layer should not contain pixel-level image processing rules, and it should not contain UI-specific code.

This makes the app easier to extend because interfaces such as CLI, desktop UI, or batch jobs can all reuse the same application workflows.

## What a Service Is

A service is an application level object or function that represents a concrete workflow.

Examples:

- render a timeslice from an image folder
- generate a low-resolution preview
- export a composite image to disk
- save metadata for a render
- run a batch of render jobs

A service should coordinate existing components rather than reimplement their logic.

For example, a render service may:

1. ask a loader for image paths
2. ask the loader to load images
3. call the domain compositor using a `TimesliceSpec`
4. return a `CompositeResult`
5. save the image through a writer

## Responsibilities of the Application Layer

The application layer should, for example:

- define use case inputs and outputs
- coordinate domain and infrastructure components
- enforce workflow level validation
- return structured responses to interfaces

The application layer should not, for example:

- perform slice planning directly
- implement compositing loops
- call `argparse` or build GUI widgets
- depend on PIL or OpenCV details more than necessary

## Why Services Matter

Without services, workflow logic tends to leak into the CLI or UI. That becomes a problem once the application has multiple entry points. A CLI, desktop app, and batch runner may all end up duplicating the same steps slightly differently.

Services solve that by creating one canonical place for each workflow. The interfaces become thin, and the behavior stays consistent across the application.

## Example Service Boundary

A `RenderTimesliceService` is a good first application service.

Its responsibility is not to know how slices are built internally. Its responsibility is to know how to perform the render workflow from input folder to final result.

Typical inputs:

- source folder
- `TimesliceSpec`
- resize mode

Typical outputs:

- `CompositeResult`
- source image paths
- later, timing or metadata

## Relationship to Other Layers

The application layer depends on the domain and on infrastructure abstractions.

A typical flow looks like this:

Interface → Application Service → Domain + Infrastructure → Result

For example:

- CLI parses arguments
- application service coordinates the render
- infrastructure loads images
- domain builds the plan and composite
- service returns the result
- CLI prints status and exits

## Extensibility

Services are a good extensibility point because they let you add workflows without changing the core domain.

For example, we can extend `pytimeslice` with the notion of 'projects' via a
`ProjectSaveService` and `ProjectLoadService`.

Each new service can reuse the same domain models and processing primitives, while exposing a different workflow.
