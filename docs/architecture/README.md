# pytimeslice Architecture

## Overview

`pytimeslice` is a layered Python library for generating time-slice composite
images from ordered image sequences.

Its purpose is to provide a reusable rendering core that can be used from:

- Python code
- a CLI
- future desktop tools
- future web services

The engine is designed so that rendering logic stays independent from interfaces and file I/O.

## Core Idea

The central contract of `pytimeslice` is:

> Given an ordered sequence of normalized RGB images and a time-slice specification, produce a deterministic composite image.

A user describes the desired render through a `TimesliceSpec`, and the engine translates that intent into a concrete slice plan and final composite.

## Architectural Layers

`pytimeslice` is organized into four layers.

### Domain

The domain layer contains the core business logic.

It defines:

- render specifications
- slice planning
- compositing behavior
- render result models

This is the most important layer in the engine and should remain independent from UI and file system concerns.

### Application

The application layer coordinates workflows.

It is responsible for use cases such as:

- rendering from a folder
- validating workflow inputs
- invoking infrastructure adapters and domain logic
- returning structured results

### Infrastructure

The infrastructure layer handles technical details such as:
- discovering image files
- decoding images
- preprocessing and normalization
- saving rendered outputs

This layer supports the engine but does not define rendering rules.

### Interfaces

The interface layer exposes the engine to external consumers.

Examples include:
- CLI commands
- future desktop UI
- future API endpoints

Interfaces should remain thin and delegate real work to the application layer or public API.

## Flow Through the System

A typical render flow looks like this:

```text
Interface -> Public API / Application Service -> Domain + Infrastructure -> Result
````

Example:

1. A caller provides an input folder and render options.
2. The application layer loads the source images through infrastructure adapters.
3. The domain layer builds a slice plan.
4. The compositor produces the final image.
5. The result is returned to the caller or written to disk.

## Key Models

Some of the main models in the system are:

- `TimesliceSpec`: describes the desired render
- `SliceBand`: describes one slice of the output
- `TimeslicePlan`: describes the full slice layout
- `CompositeResult`: contains the final image and traceable metadata

These models define the vocabulary of the engine.

## Design Priorities

`pytimeslice` emphasizes:

- deterministic output
- clean separation of concerns
- testable rendering logic
- reusable library design
- extensibility for future workflows

## Future Growth

The architecture is intended to support future additions such as:

- preview rendering
- metadata export
- batch rendering
- alternate frame selection strategies
- tighter integration with future applications built on top of `pytimeslice`

The goal is to extend the system without rewriting the core rendering logic.
