# Interface Layer

## Purpose

The interface layer exposes `pytimeslice` to external consumers. It is the
outermost layer of the system and is responsible for translating user or caller
interaction into internal engine calls.

Its job is to handle concerns such as command-line argument parsing, future desktop UI input, API request handling, status output, and error presentation. Each of the previous interaction styles listed would typically be represented by a distinct interface in the interface layer. This layer should not contain slice planning rules, compositing logic, or technical file handling beyond what is needed to hand work off to the engine.

This makes the app easier to extend because new ways of interacting with the engine can be added without changing the core rendering or workflow logic.

## What the Interface Layer Is

The interface layer is the part of the system that translates interaction into internal requests.

Examples:

* a CLI command
* a desktop UI form
* an API endpoint
* a notebook-facing wrapper
* user-facing status messages
* formatted error output

An interface should collect input and delegate work rather than reimplement the engine.

For example, a CLI interface may:

1. parse command-line arguments
2. construct a `TimesliceSpec`
3. call a public API function or application service
4. receive a structured result
5. display success or failure to the user

## Responsibilities of the Interface Layer

The interface layer should, for example:

* gather and parse user or caller input
* translate input into internal models or requests
* invoke the public API or application layer
* format outputs for the caller
* present errors in a user-appropriate way
* remain thin and easy to replace

The interface layer should not, for example:

* define what a valid time-slice means
* perform slice planning
* implement compositing loops
* decode images with Pillow or OpenCV
* coordinate low-level workflow details already handled elsewhere

## Why the Interface Layer Matters

Without a clear interface layer, user-facing code tends to absorb workflow logic, technical I/O, or even rendering rules. That makes the system harder to maintain and harder to reuse across different entry points.

The interface layer solves that by creating one canonical place for interaction logic. The rest of the system can then stay focused on workflows, rendering, and infrastructure rather than on how commands or requests are presented.

## Example Interface Boundary

A CLI module is a good example of an interface.

Its responsibility is not to know how a time-slice is rendered internally. Its responsibility is to collect input, construct the right request, invoke the engine, and present the result clearly.

Typical inputs:

* file paths
* orientation
* slice count
* resize mode
* reverse-time flag

Typical outputs:

* printed status messages
* formatted error messages
* process exit behavior
* a successful call into the engine

## Relationship to Other Layers

The interface layer depends on the public API or application layer and should remain thin.

A typical flow looks like this:

Interface → Public API / Application Service → Domain + Infrastructure → Result

For example:

* interface gathers input from the user
* application coordinates the workflow
* infrastructure loads or saves files
* domain builds the plan and composite
* application returns the result
* interface presents the result to the caller

## Extensibility

The interface layer is a good extensibility point because it lets you add new ways of interacting with the engine without changing the core logic.

For example, we can extend `pytimeslice` with a richer CLI, a desktop
interface, notebook helpers, or a web API.

Each new interface can reuse the same public API, application workflows, and domain models while changing only how the engine is exposed to users or external systems.
