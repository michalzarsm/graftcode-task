# Graftcode Documentation — Consolidated Markdown Guide

**Generated:** 2026-05-22  
**Source:** Official Graftcode documentation at `docs.dev.graftcode.com`  
**Format:** Readable, organized Markdown consolidation  

> This document is a structured, paraphrased consolidation of the Graftcode documentation. It preserves the official topic order, key concepts, examples, commands, constraints, and recommended patterns, while linking each section back to its original source page.

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Source index](#2-source-index)
3. [Introduction](#3-introduction)
   - [3.1 What is Graftcode?](#31-what-is-graftcode)
   - [3.2 What problem does Graftcode solve?](#32-what-problem-does-graftcode-solve)
   - [3.3 Where Graftcode fits](#33-where-graftcode-fits)
   - [3.4 When to use Graftcode](#34-when-to-use-graftcode)
4. [Core concepts](#4-core-concepts)
   - [4.1 What is a Graft?](#41-what-is-a-graft)
   - [4.2 Public interface vs. business logic](#42-public-interface-vs-business-logic)
   - [4.3 Caller and receiver](#43-caller-and-receiver)
   - [4.4 Graftcode Gateway](#44-graftcode-gateway)
   - [4.5 Hypertube runtime bridge](#45-hypertube-runtime-bridge)
   - [4.6 Graftcode Vision](#46-graftcode-vision)
5. [How Graftcode works](#5-how-graftcode-works)
   - [5.1 Development-time vs. production-time behavior](#51-development-time-vs-production-time-behavior)
   - [5.2 What goes to Graftcode Cloud](#52-what-goes-to-graftcode-cloud)
   - [5.3 How Grafts are generated](#53-how-grafts-are-generated)
   - [5.4 Runtime call execution](#54-runtime-call-execution)
   - [5.5 Local, remote, and in-memory execution](#55-local-remote-and-in-memory-execution)
   - [5.6 Observability, tracing, and context propagation](#56-observability-tracing-and-context-propagation)
   - [5.7 Scaling, load balancers, and proxies](#57-scaling-load-balancers-and-proxies)
   - [5.8 What happens when interfaces change](#58-what-happens-when-interfaces-change)
   - [5.9 Alpha limitations and known constraints](#59-alpha-limitations-and-known-constraints)
6. [Integration patterns](#6-integration-patterns)
   - [6.1 Service-to-service integration](#61-service-to-service-integration)
   - [6.2 Edge clients without APIs](#62-edge-clients-without-apis)
   - [6.3 Internal business APIs](#63-internal-business-apis)
   - [6.4 MCP hosting and AI tools](#64-mcp-hosting-and-ai-tools)
   - [6.5 Modular monoliths](#65-modular-monoliths)
   - [6.6 Microservices without contracts](#66-microservices-without-contracts)
   - [6.7 Event-driven communication preview](#67-event-driven-communication-preview)
7. [Security and trust](#7-security-and-trust)
   - [7.1 Security model overview](#71-security-model-overview)
   - [7.2 Authentication and authorization](#72-authentication-and-authorization)
   - [7.3 Security plugins](#73-security-plugins)
   - [7.4 Transport security: TLS/WSS](#74-transport-security-tlswss)
   - [7.5 Network boundaries and isolation](#75-network-boundaries-and-isolation)
   - [7.6 Enterprise self-hosted engine](#76-enterprise-self-hosted-engine)
8. [Performance and efficiency](#8-performance-and-efficiency)
   - [8.1 Compare Performance](#81-compare-performance)
   - [8.2 Why runtime-level integration is faster](#82-why-runtime-level-integration-is-faster)
   - [8.3 REST vs. gRPC vs. Graftcode](#83-rest-vs-grpc-vs-graftcode)
   - [8.4 CPU, memory, and network usage](#84-cpu-memory-and-network-usage)
   - [8.5 Cloud cost implications](#85-cloud-cost-implications)
   - [8.6 When performance gains matter](#86-when-performance-gains-matter)
9. [Quick reference](#9-quick-reference)
10. [Practical adoption checklist](#10-practical-adoption-checklist)
11. [Glossary](#11-glossary)

---

# 1. Executive summary

Graftcode is a runtime-level integration platform. Its central idea is that software should be able to communicate through the same kind of public programming interfaces developers already write: public classes, public methods, method signatures, argument types, return types, exceptions, callbacks, and object lifecycles.

Instead of designing a separate API contract, generating a separate schema, building a separate client library, and maintaining adapters around business logic, Graftcode turns public code interfaces into installable, strongly typed client packages called **Grafts**. A Graft allows one application to consume another module as though it were a local dependency, even when the implementation runs in a different runtime, process, host, or language.

The execution model is built around three important pieces:

| Component | Purpose |
|---|---|
| **Graft** | A generated, native client package that exposes another module’s public interface to a caller. |
| **Graftcode Gateway** | A lightweight runtime host that loads modules, inspects their public interfaces, exposes them through Hypertube, and provides metadata to the Graftcode Cloud for generation. |
| **Hypertube** | A runtime bridge that carries invocation intent between callers and receivers, either in memory, across runtimes, or over the network. |

A fourth tool, **Graftcode Vision**, helps developers inspect exposed types and methods, try calls interactively, and copy package-manager commands and configuration examples.

The platform is designed to fit beside existing infrastructure rather than replace it. It can coexist with REST, gRPC, message queues, service meshes, load balancers, reverse proxies, observability stacks, TLS, and security systems. Its distinctive claim is that integration can be treated as runtime-level method invocation rather than protocol-level endpoint design.

The documentation repeatedly emphasizes several principles:

- **Public interfaces are the contract.** Business logic stays private; only public method shapes are exposed.
- **Graftcode Cloud is not in the production execution path.** Cloud services help generate Grafts and store interface metadata, but runtime calls go directly between the caller and receiver through Hypertube/Gateway.
- **Only interface metadata is sent to the cloud.** Source code, binaries, secrets, runtime data, arguments, return values, and exceptions are not sent for normal Graft generation.
- **Architecture can change through configuration.** The same call can run in memory, across runtimes, across processes, or remotely, depending on routing and connection settings.
- **Alpha limitations matter.** The current Alpha has restrictions around supported type shapes, async wrappers, inheritance, stateful objects, browser/network behavior, package dependencies, and authentication plugin support.

---

# 2. Source index

The following table lists the source pages used to build this guide, preserving the official documentation order.

| Section | Page | Source URL |
|---|---|---|
| Introduction | What is Graftcode | `https://docs.dev.graftcode.com/documentation/introduction/what-is-graftcode` |
| Introduction | What problem does Graftcode solve | `https://docs.dev.graftcode.com/documentation/introduction/what-problem-does-graftcode-solve` |
| Introduction | Where Graftcode fits | `https://docs.dev.graftcode.com/documentation/introduction/where-graftcode-fits` |
| Introduction | When to use Graftcode | `https://docs.dev.graftcode.com/documentation/introduction/when-to-use-graftcode` |
| Core Concepts | What is a Graft | `https://docs.dev.graftcode.com/documentation/core-concepts/what-is-a-graft` |
| Core Concepts | Public Interface vs Business Logic | `https://docs.dev.graftcode.com/documentation/core-concepts/public-interface-vs-business-logic` |
| Core Concepts | Caller and Receiver | `https://docs.dev.graftcode.com/documentation/core-concepts/caller-and-receiver` |
| Core Concepts | Graftcode Gateway | `https://docs.dev.graftcode.com/documentation/core-concepts/graftcode-gateway` |
| Core Concepts | Hypertube Runtime Bridge | `https://docs.dev.graftcode.com/documentation/core-concepts/hypertube-runtime-bridge` |
| Core Concepts | Graftcode Vision | `https://docs.dev.graftcode.com/documentation/core-concepts/graftcode-vision` |
| How Graftcode Works | Development-time vs production-time behavior | `https://docs.dev.graftcode.com/documentation/how-graftcode-works/development-time-vs-production-time` |
| How Graftcode Works | What goes to Graftcode Cloud | `https://docs.dev.graftcode.com/documentation/how-graftcode-works/what-goes-to-graftcode-cloud` |
| How Graftcode Works | How Grafts are generated | `https://docs.dev.graftcode.com/documentation/how-graftcode-works/how-grafts-are-generated` |
| How Graftcode Works | Runtime call execution | `https://docs.dev.graftcode.com/documentation/how-graftcode-works/runtime-call-execution` |
| How Graftcode Works | Local, remote, and in-memory execution | `https://docs.dev.graftcode.com/documentation/how-graftcode-works/local-remote-and-in-memory-execution` |
| How Graftcode Works | Observability, tracing, and context propagation | `https://docs.dev.graftcode.com/documentation/how-graftcode-works/observability-tracing-and-context-propagation` |
| How Graftcode Works | Scaling, load balancers, and proxies | `https://docs.dev.graftcode.com/documentation/how-graftcode-works/scaling-load-balancers-and-proxies` |
| How Graftcode Works | What happens when interfaces change | `https://docs.dev.graftcode.com/documentation/how-graftcode-works/what-happens-when-interfaces-change` |
| How Graftcode Works | Alpha limitations and known constraints | `https://docs.dev.graftcode.com/documentation/how-graftcode-works/alpha-limitations-and-known-constraints` |
| Integration Patterns | Service-to-Service Integration | `https://docs.dev.graftcode.com/documentation/integration-patterns/service-to-service-integration` |
| Integration Patterns | Edge Clients Without APIs | `https://docs.dev.graftcode.com/documentation/integration-patterns/edge-clients-without-apis` |
| Integration Patterns | Internal Business APIs | `https://docs.dev.graftcode.com/documentation/integration-patterns/internal-business-apis` |
| Integration Patterns | MCP Hosting and AI Tools | `https://docs.dev.graftcode.com/documentation/integration-patterns/mcp-hosting-and-ai-tools` |
| Integration Patterns | Modular Monoliths | `https://docs.dev.graftcode.com/documentation/integration-patterns/modular-monoliths` |
| Integration Patterns | Microservices Without Contracts | `https://docs.dev.graftcode.com/documentation/integration-patterns/microservices-without-contracts` |
| Integration Patterns | Event-Driven Communication Preview | `https://docs.dev.graftcode.com/documentation/integration-patterns/event-driven-communication-preview` |
| Security and Trust | Security Model Overview | `https://docs.dev.graftcode.com/documentation/security-and-trust/security-model-overview` |
| Security and Trust | Authentication and Authorization | `https://docs.dev.graftcode.com/documentation/security-and-trust/authentication-and-authorization` |
| Security and Trust | Security Plugins | `https://docs.dev.graftcode.com/documentation/security-and-trust/security-plugins` |
| Security and Trust | Transport Security TLS/WSS | `https://docs.dev.graftcode.com/documentation/security-and-trust/transport-security-tls-wss` |
| Security and Trust | Network Boundaries and Isolation | `https://docs.dev.graftcode.com/documentation/security-and-trust/network-boundaries-and-isolation` |
| Security and Trust | Enterprise Self-Hosted Engine | `https://docs.dev.graftcode.com/documentation/security-and-trust/enterprise-self-hosted-engine` |
| Performance and Efficiency | Compare Performance | `https://docs.dev.graftcode.com/documentation/performance-and-efficiency/compare-performance` |
| Performance and Efficiency | Why Runtime-Level Integration is Faster | `https://docs.dev.graftcode.com/documentation/performance-and-efficiency/why-runtime-level-integration-is-faster` |
| Performance and Efficiency | REST vs gRPC vs Graftcode | `https://docs.dev.graftcode.com/documentation/performance-and-efficiency/rest-vs-grpc-vs-graftcode` |
| Performance and Efficiency | CPU, Memory, and Network Usage | `https://docs.dev.graftcode.com/documentation/performance-and-efficiency/cpu-memory-and-network-usage` |
| Performance and Efficiency | Cloud Cost Implications | `https://docs.dev.graftcode.com/documentation/performance-and-efficiency/cloud-cost-implications` |
| Performance and Efficiency | When Performance Gains Matter | `https://docs.dev.graftcode.com/documentation/performance-and-efficiency/when-performance-gains-matter` |
| Reference | Quick Reference | `https://docs.dev.graftcode.com/documentation/reference/quick-reference` |

---

# 3. Introduction

## 3.1 What is Graftcode?

**Source:** `https://docs.dev.graftcode.com/documentation/introduction/what-is-graftcode`

Graftcode is a platform for integrating software through runtime-level programming interfaces. It allows a public method from one module, service, or application to be called from another environment using a generated native package rather than a manually designed API endpoint.

The core idea is simple:

> A public method can become an integration surface.

In a conventional system, a developer often writes business logic and then adds a second layer to expose that logic: controllers, DTOs, OpenAPI schemas, protobuf files, route definitions, adapters, generated stubs, client SDKs, and versioned documentation. Graftcode attempts to remove much of that duplicate integration work by letting the existing public interface become the contract.

A service can expose public classes and methods. A consuming application installs a Graft package, imports or references it like a normal dependency, and calls methods with native syntax. The implementation may run locally, in another runtime, in another process, or remotely over the network.

### Core idea

| Traditional integration | Graftcode-style integration |
|---|---|
| Define HTTP/gRPC/message contract separately from code | Public methods and types define the callable surface |
| Generate or hand-write clients | Install generated Graft packages through package managers |
| Route by URL/topic/procedure name | Route by runtime invocation intent |
| Translate between protocol objects and business objects | Preserve method calls and type shapes as much as possible |
| Change architecture through endpoint and client changes | Change topology primarily through configuration |

### Main promise

Graftcode aims to make distributed systems feel closer to ordinary programming. It does not claim that distribution disappears. Latency, failures, versioning, security, observability, and topology still matter. The goal is to make the integration surface smaller and more natural for developers.

---

## 3.2 What problem does Graftcode solve?

**Source:** `https://docs.dev.graftcode.com/documentation/introduction/what-problem-does-graftcode-solve`

Software teams frequently build two parallel systems:

1. The actual business logic.
2. The integration machinery that exposes that logic to other systems.

That second system includes API contracts, serializers, schema definitions, generated stubs, endpoint routing, controller layers, client libraries, compatibility work, error mapping, auth hooks, and documentation. It is necessary in many architectures, but it can become expensive to design, maintain, version, and test.

Graftcode addresses this by turning public interfaces into consumable packages. Instead of translating business logic into a separate protocol contract, Graftcode builds a model of the public interface and generates a native caller-side package.

### Problems Graftcode targets

| Problem | What Graftcode changes |
|---|---|
| Duplicate contracts | Public code interfaces become the primary contract. |
| Client library drift | Grafts are generated from the current interface model. |
| Manual adapters | Calls are represented as runtime invocation intent. |
| Cross-language friction | A module can be consumed from another supported runtime through generated native packages. |
| Internal API overhead | Internal systems can call public methods without designing a separate REST/gRPC layer. |
| Refactor hesitation | Interface changes can be handled similarly to package versioning. |

### What it does not eliminate

Graftcode does not remove the need to think about:

- security and authorization,
- network failures,
- latency,
- version compatibility,
- stateful object lifecycles,
- observability,
- deployment topology,
- load balancing,
- infrastructure policy.

It changes how integration is represented and generated, not the physical realities of distributed computing.

---

## 3.3 Where Graftcode fits

**Source:** `https://docs.dev.graftcode.com/documentation/introduction/where-graftcode-fits`

Graftcode fits between application code and infrastructure. It is not a full replacement for existing web frameworks, API gateways, cloud platforms, service meshes, security systems, package managers, or observability tools. It is an integration layer that can sit alongside those systems.

### Conceptual placement

```text
Application code
  ↓
Public classes, methods, and types
  ↓
Graftcode Gateway + Hypertube
  ↓
Generated Grafts / runtime invocation
  ↓
Existing infrastructure: networks, proxies, load balancers, TLS, observability, deployment platforms
```

### What Graftcode can coexist with

| Existing technology | Relationship to Graftcode |
|---|---|
| REST APIs | Can continue to exist for public APIs, external clients, or compatibility. |
| gRPC | Can coexist where explicit protobuf contracts or high-performance RPC are desired. |
| Message queues | Can be used through transport plugins or existing application code. |
| Load balancers | Used for remote Hypertube/Gateway connections. |
| Reverse proxies | Can front WebSocket/TLS traffic. |
| Service meshes | Can provide network policy, routing, observability, or mTLS around Graftcode traffic. |
| OpenTelemetry | Can receive propagated context and traces. |
| Package managers | Used to distribute generated Grafts. |

### Practical interpretation

Graftcode is most useful when the team controls both sides of an integration and wants to reduce endpoint/schema/client maintenance. Public internet APIs may still benefit from explicit REST or gRPC contracts, depending on audience and governance needs.

---

## 3.4 When to use Graftcode

**Source:** `https://docs.dev.graftcode.com/documentation/introduction/when-to-use-graftcode`

Graftcode is strongest where integration is internal, frequent, evolving, and developer-to-developer. It is less compelling for one-off integrations or cases where an explicit public protocol is the product.

### Good fits

| Use case | Why it fits |
|---|---|
| Internal service-to-service calls | Teams can expose public methods instead of maintaining separate internal APIs. |
| Modular monoliths | Modules can start in memory and later move across processes or hosts. |
| Polyglot systems | A module in one runtime can be consumed as a package in another. |
| Internal business APIs | Public facades can represent business capabilities directly. |
| Edge clients | Browser, mobile, or desktop clients can consume backend capabilities through typed packages, subject to security and network constraints. |
| AI/MCP tools | Public methods can be exposed as callable tools without creating a separate AI-only surface. |

### Weaker fits

| Use case | Reason |
|---|---|
| Simple stable public REST API | Existing API contract may be sufficient and expected by consumers. |
| Public third-party platform API | External consumers may need long-lived protocol documentation and governance. |
| One-off import/export | A batch script or data pipeline may be simpler. |
| Very low-traffic systems | Performance and maintenance gains may not justify a new integration model. |
| Systems where all integration is already standardized | Existing gRPC/OpenAPI contracts may already be mature and stable. |

### Adoption posture

Graftcode can be introduced incrementally. A team can expose one module, generate one Graft, and route calls locally before moving anything across a network. This is important because it avoids a “big rewrite” migration path.

---

# 4. Core concepts

## 4.1 What is a Graft?

**Source:** `https://docs.dev.graftcode.com/documentation/core-concepts/what-is-a-graft`

A **Graft** is a generated, strongly typed client package that allows a caller to use another module’s public interface as though it were a native dependency.

A Graft can represent a module written in another language, running in another runtime, or located on another machine. It is distributed through normal package managers such as npm, NuGet, PyPI, or Maven-style ecosystems, depending on the target runtime.

### What a Graft contains

A Graft normally contains:

- generated classes, methods, and type definitions that mirror the exposed public interface,
- Hypertube bindings that convert local calls into runtime invocation intent,
- configuration hooks for routing calls to the right receiver,
- mappings for exceptions and return values,
- package metadata for normal dependency management.

A Graft does **not** contain the remote module’s private implementation or business logic.

### Example package naming

The documentation describes registry and package naming conventions similar to the following:

```text
Free registry:
http://grft.dev/<random-guid>__free

Project registry:
http://grft.dev/<project-id>__graftcode

Package naming pattern:
graft.<technology_package>.<ModuleName>
```

For example, a .NET module named `EnergyPrice.dll` could be exposed as a Graft package named:

```text
graft.nuget.EnergyPrice
```

The same module might also be consumable from npm as a package named similarly to:

```text
@graft/nuget-EnergyPrice
```

### Example installation commands

```bash
dotnet add package graft.nuget.EnergyPrice --source http://grft.dev/<project-id>__graftcode
```

```bash
npm install @graft/nuget-EnergyPrice --registry=http://grft.dev/<project-id>__graftcode
```

### Example configuration

```js
GraftConfig.host = "tcp://energy-service:9000";
```

```js
GraftConfig.setConfig(
  "name=@graft/nuget-EnergyPrice;runtime=netcore;host=ws://localhost:8004/ws"
);
```

The documentation notes that complete connection-string style configuration is not fully supported in the current release, so Alpha users should check current runtime-specific behavior.

---

## 4.2 Public interface vs. business logic

**Source:** `https://docs.dev.graftcode.com/documentation/core-concepts/public-interface-vs-business-logic`

Graftcode distinguishes sharply between what is callable and what is private.

The **public interface** is made up of public classes, methods, signatures, argument types, return types, overloads, and other exposed type information. The **business logic** is the implementation behind those public methods.

Graftcode uses the public interface to generate Grafts. It does not need to send private implementation code to the cloud to do that.

### Practical design rule

Treat Graft-exposed code like a library API:

- expose stable, intentional public methods,
- keep private implementation details private,
- use facade classes to define a clean boundary,
- avoid exposing every internal type by accident,
- version public surfaces deliberately.

### Stateless and stateful interfaces

Graftcode can conceptually support both stateless and stateful programming models.

| Model | Description | Best suited for |
|---|---|---|
| Stateless | A call does not depend on object identity or previous interactions. Static methods and pure service facades fit here. | Request-response business capabilities, edge clients, internal APIs. |
| Stateful | Calls can depend on object lifetimes, references, callbacks, events, or workflow context. | Sessions, long-running workflows, interactive tools, object-oriented models. |

In the Alpha release, stateful behavior has important deployment implications. Returned objects may represent remote state, and accessing their properties can create additional backend calls. Load balancing for stateful objects may require sticky sessions or careful routing.

---

## 4.3 Caller and receiver

**Source:** `https://docs.dev.graftcode.com/documentation/core-concepts/caller-and-receiver`

Graftcode uses the terms **caller** and **receiver** instead of fixed “client” and “server” roles.

A caller is the side that invokes a method. A receiver is the side that executes the method. The same application can be a caller in one interaction and a receiver in another.

### Why this matters

Traditional terminology can imply a fixed architecture:

```text
client → server
```

Graftcode’s model is more dynamic:

```text
caller → receiver
receiver → caller callback
service A → service B
service B → service C
edge app → backend module
backend module → AI tool host
```

This framing is useful because Graftcode supports duplex and object-oriented interactions. A receiver can later call back into a caller if the exposed interface and routing support it.

### Method calls, not messages

Although calls may travel over a network, the developer-facing model is method invocation rather than endpoint messaging. The transport layer carries an invocation intent: which method to call, with which arguments, in which context, and how to return results or exceptions.

---

## 4.4 Graftcode Gateway

**Source:** `https://docs.dev.graftcode.com/documentation/core-concepts/graftcode-gateway`

The **Graftcode Gateway** is a lightweight native runtime host. It loads modules, inspects their public interfaces, makes them available through Hypertube, and provides a public-interface model to Graftcode Cloud for package generation.

It is not a reverse proxy and not a traditional API gateway. It is closer to a runtime host plus integration boundary.

### Gateway responsibilities

| Responsibility | Description |
|---|---|
| Load runtimes | Host or attach to supported runtimes such as CLR, JVM, Python, or other supported environments. |
| Load modules | Make application libraries available for inspection and execution. |
| Analyze public interfaces | Discover public classes, methods, signatures, and types. |
| Build UGM | Create a Unified Graft Model representing the exposed public surface. |
| Provide metadata to cloud | Send interface metadata needed to generate packages. |
| Host Hypertube | Accept and execute invocation intent through the embedded runtime bridge. |
| Support Vision | Provide data for the developer-facing interface explorer. |

### What the Gateway does not do

The Gateway does not generate Grafts by itself. Generation is handled through the Graftcode Cloud/registry process. The Gateway also does not send business logic, source code, private code, or runtime payloads to the cloud for normal package generation.

### Unified Graft Model and IIP

Two recurring terms are attached to the Gateway:

- **UGM — Unified Graft Model:** a structured representation of public classes, methods, signatures, and types.
- **IIP — Intention Invocation Protocol:** a binary representation of programming intent used by Hypertube to carry calls.

### Operational role

The Gateway is the explicit entry point for remote calls into a module. In a production deployment, one or more Gateways can sit behind standard load balancers, reverse proxies, ingress controllers, or service mesh infrastructure.

---

## 4.5 Hypertube runtime bridge

**Source:** `https://docs.dev.graftcode.com/documentation/core-concepts/hypertube-runtime-bridge`

**Hypertube** is the runtime bridge that moves method invocation intent between caller and receiver.

It is responsible for turning a local method call made through a Graft into something that can be executed by the target runtime, then returning results or exceptions to the caller.

### Execution modes

Hypertube can support several topologies:

| Mode | Meaning |
|---|---|
| In-memory | Caller and receiver are in the same process or compatible runtime context. |
| Local cross-runtime | Caller and receiver are on the same machine or process boundary but use different runtimes. |
| Remote | Caller and receiver communicate over TCP/IP or WebSocket-style transports. |
| Plugin-routed | Invocation intent is routed through a custom transport, queue, broker, or policy layer. |

### What Hypertube carries

Hypertube carries invocation intent rather than a conventional HTTP request. That intent includes the target type or method, arguments, context, execution metadata, and the mechanism for returning results or errors.

### Why it matters

Because Graftcode works at the runtime-call level, it can avoid some of the repeated translation layers typical in protocol-first integration. It still uses transports when needed, but the developer-facing abstraction remains a method call.

---

## 4.6 Graftcode Vision

**Source:** `https://docs.dev.graftcode.com/documentation/core-concepts/graftcode-vision`

**Graftcode Vision** is a developer tool for inspecting and trying the public interfaces exposed by a Gateway.

It is analogous in spirit to API exploration tools such as Swagger UI or Postman, but the unit of exploration is a public method rather than an HTTP endpoint.

### What Vision shows

Vision can help developers see:

- exposed public classes,
- public methods,
- argument and return types,
- overloads,
- package manager install commands,
- runtime configuration examples,
- generated usage samples,
- interactive method execution surfaces.

### What Vision is for

Vision helps answer practical questions:

- What can this module expose?
- Which package should I install?
- How do I configure the caller to reach the receiver?
- What does a sample method call look like?
- Does this method execute as expected?

### Security posture

Vision does not bypass the runtime security model. It exposes what the Gateway exposes and is subject to the same authentication, authorization, transport, and network rules as the rest of the system.

---

# 5. How Graftcode works

## 5.1 Development-time vs. production-time behavior

**Source:** `https://docs.dev.graftcode.com/documentation/how-graftcode-works/development-time-vs-production-time`

Graftcode behaves differently during development and production.

During development, the emphasis is on discovery, package generation, and tooling. During production, the emphasis is on direct runtime execution between caller and receiver.

### Development-time flow

```text
Developer starts Gateway
  ↓
Gateway loads modules and runtimes
  ↓
Gateway discovers public interfaces
  ↓
Gateway builds UGM metadata
  ↓
Graftcode Cloud/registry can generate Grafts
  ↓
Developer installs package and writes normal code
```

Development-time work includes interface discovery, Vision inspection, package-manager commands, generated client packages, configuration examples, and fast feedback when public interfaces change.

### Production-time flow

```text
Caller imports generated Graft
  ↓
Caller invokes method
  ↓
Graft converts call into invocation intent
  ↓
Hypertube routes call to configured receiver
  ↓
Gateway executes target method
  ↓
Result or exception returns to caller
```

In production, Graftcode Cloud is not the runtime mediator. Calls are not proxied through the cloud. The generated Graft communicates with the configured Gateway/Hypertube endpoint or in-memory receiver according to configuration.

### Comparison table

| Area | Development time | Production time |
|---|---|---|
| Main purpose | Discover interfaces and generate packages | Execute calls |
| Cloud role | Metadata and package generation | Not in the call path |
| Developer tool | Vision, package install commands, examples | Runtime config, logs, tracing |
| Data involved | Public interface metadata | Invocation intent and runtime payloads between caller/receiver |
| Failure impact | May affect new package generation | Existing configured calls continue if runtime infrastructure is available |

---

## 5.2 What goes to Graftcode Cloud

**Source:** `https://docs.dev.graftcode.com/documentation/how-graftcode-works/what-goes-to-graftcode-cloud`

Graftcode Cloud needs enough metadata to generate client packages. It does not need the implementation of the exposed module.

### Sent to Graftcode Cloud

The Gateway can send interface metadata such as:

- public class names,
- public method names,
- method signatures,
- argument types,
- return types,
- structural type information,
- version and package-generation metadata,
- package request information.

The cloud may also receive optional high-level aggregate information, depending on configuration, such as package activity, usage counts, or version adoption data.

### Not sent to Graftcode Cloud for normal generation

The documentation emphasizes that the following are not sent for normal Graft generation:

- business logic,
- source code,
- compiled binaries,
- private methods,
- private classes,
- runtime arguments,
- return values,
- exceptions,
- secrets,
- environment variables,
- live production traffic.

### Practical trust boundary

The cloud is used to generate and distribute Graft packages. Production execution stays within the caller/receiver environment. This separation is central to Graftcode’s security and operational model.

---

## 5.3 How Grafts are generated

**Source:** `https://docs.dev.graftcode.com/documentation/how-graftcode-works/how-grafts-are-generated`

Graft generation begins when a Gateway exposes a public interface model. The cloud registry uses that model to build native packages for consuming runtimes.

### Generation flow

```text
Gateway loads module
  ↓
Gateway creates UGM from public interfaces
  ↓
UGM metadata is registered
  ↓
Caller requests package through npm/NuGet/PyPI/etc.
  ↓
Graftcode generation engine identifies target language/runtime
  ↓
Typed Graft package is generated or retrieved from cache
  ↓
Caller installs Graft as a normal dependency
```

### What generated packages include

A generated Graft usually includes:

- language-native type definitions,
- methods mirroring the exposed public interface,
- Hypertube invocation bindings,
- runtime configuration hooks,
- result and exception handling,
- package metadata.

It does not include the receiver’s business logic.

### CI/CD use

Because Grafts are normal packages, they can be used in build pipelines like other dependencies. Teams can pin versions, use version ranges, run tests against generated clients, and validate that expected public interfaces still exist.

### Interface changes and regeneration

When public interfaces change, a new or refreshed model can be registered. Consumers may update their package versions just as they would update a normal library dependency.

---

## 5.4 Runtime call execution

**Source:** `https://docs.dev.graftcode.com/documentation/how-graftcode-works/runtime-call-execution`

At runtime, a Graft turns a native method call into invocation intent and sends it through Hypertube to the receiver.

### Execution sequence

```text
Application calls generated method
  ↓
Graft captures target method, arguments, and context
  ↓
Call becomes IIP invocation intent
  ↓
Hypertube chooses route based on configuration
  ↓
Receiver Gateway executes target method
  ↓
Result, exception, callback, or event returns through Hypertube
  ↓
Caller receives native result or error
```

### Configuration priority

The documentation describes routing as being controlled by Graft connection configuration. The precedence is summarized as:

| Priority | Configuration source |
|---:|---|
| 1 | Runtime-specific environment variable |
| 2 | Global environment variable |
| 3 | Runtime-specific configuration file |
| 4 | Global configuration file |
| 5 | User code |
| 6 | Graft package default |
| 7 | Hypertube default, often in-memory |

Per-Graft configuration can override global configuration.

### What can be routed

A call can be routed to:

- the same runtime,
- another runtime in the same process or environment,
- another process,
- a remote host over TCP/IP or WebSocket,
- a transport or security plugin,
- an in-memory receiver.

### Results and errors

Hypertube handles normal return values, exceptions, synchronous calls, asynchronous patterns, callbacks, events, stateful object lifecycles, and execution context as supported by the runtime and current release.

---

## 5.5 Local, remote, and in-memory execution

**Source:** `https://docs.dev.graftcode.com/documentation/how-graftcode-works/local-remote-and-in-memory-execution`

One of Graftcode’s main design points is that a caller’s code can remain stable while the execution topology changes.

The same method call can be resolved in memory, across a local runtime boundary, or remotely by changing configuration rather than rewriting the call site.

### Execution modes

| Mode | Description | Typical use |
|---|---|---|
| In-memory | Caller and receiver are colocated. Calls avoid network transport. | Modular monoliths, local development, early adoption. |
| Local multi-runtime | Different runtimes run on the same machine or process boundary. | Polyglot modules, runtime isolation. |
| Remote TCP/IP | Caller reaches a Gateway over network sockets. | Service-to-service integration. |
| Remote WebSocket/WSS | Caller uses WebSocket-style transport, often required by browsers. | Edge clients, web apps, proxy-friendly environments. |
| Plugin-routed | Transport is handled by a custom plugin or broker. | Queues, topics, enterprise routing, async delivery. |

### Incremental migration example

```text
Step 1: Module runs in memory inside one application.
Step 2: Module moves to a separate runtime on the same host.
Step 3: Module moves to a separate process.
Step 4: Module moves to a remote service behind a Gateway.
Step 5: Multiple receiver instances are placed behind a load balancer.
```

The caller continues to use the Graft package. Routing and deployment change around it.

---

## 5.6 Observability, tracing, and context propagation

**Source:** `https://docs.dev.graftcode.com/documentation/how-graftcode-works/observability-tracing-and-context-propagation`

Graftcode treats observability as part of execution context. When a call crosses runtime or network boundaries, trace information, correlation data, and execution scope can be propagated with the invocation.

### Supported observability ideas

| Concept | Meaning |
|---|---|
| Trace context | The overall distributed trace can continue across Graft calls. |
| Span context | A call can be represented as a span or sub-operation. |
| Correlation IDs | Identifiers can travel with calls to connect logs and events. |
| Scope/context | Runtime or request-level context can be preserved where supported. |
| Gateway metrics | Gateways can expose useful operational metrics depending on setup. |

### Tooling relationship

Graftcode is not positioned as a proprietary observability backend. It can integrate with existing tools such as OpenTelemetry-based pipelines, cloud observability platforms, logging systems, and self-hosted tracing tools.

### Why context propagation matters

Without context propagation, Graft calls would look like disconnected operations. With context propagation, developers and operators can follow a logical request across runtime and service boundaries.

---

## 5.7 Scaling, load balancers, and proxies

**Source:** `https://docs.dev.graftcode.com/documentation/how-graftcode-works/scaling-load-balancers-and-proxies`

Graftcode uses standard infrastructure patterns for scaling remote receivers. Gateways can sit behind load balancers, proxies, ingress controllers, or service mesh components.

### Stateless calls

Stateless calls are easiest to scale. Any equivalent receiver instance can handle the request, so ordinary load balancing generally works.

```text
Caller → Load balancer → Gateway instance A/B/C → Receiver method
```

### Stateful calls

Stateful calls need more care. If a caller holds a logical object reference or session, later calls may need to reach the same backend instance or state owner.

Common approaches include:

- sticky sessions,
- connection affinity,
- consistent hashing,
- WebSocket-aware routing,
- explicit session routing,
- moving state to shared storage where appropriate.

### Proxies and service meshes

Graftcode traffic can pass through infrastructure that supports TCP/IP, WebSocket, TLS, WSS, and related routing policies. Reverse proxies and service meshes can provide authentication, routing, observability, mTLS, or network policy, depending on deployment choices.

### Transport plugins

For advanced cases, transport plugins can route invocation intent through message brokers, queues, topics, or other enterprise messaging systems. This can enable asynchronous delivery, fan-out, delayed processing, retry policies, or transactional systems while preserving the programming-facing method model.

---

## 5.8 What happens when interfaces change

**Source:** `https://docs.dev.graftcode.com/documentation/how-graftcode-works/what-happens-when-interfaces-change`

Graftcode treats exposed public interfaces similarly to shared library APIs. Compatible changes can be adopted gradually. Breaking changes should become explicit version changes.

### Compatible changes

Examples of changes that are usually easier to support include:

- adding new methods,
- adding new overloads,
- adding optional parameters where supported,
- adding new facade classes,
- expanding return types in compatible ways.

Older Grafts can often continue working if the methods they depend on still exist with compatible signatures.

### Breaking changes

Breaking changes include:

- removing a method,
- renaming a public class or method,
- changing a method signature incompatibly,
- changing argument or return types incompatibly,
- changing behavior in a way callers do not expect.

Breaking changes should produce new package versions or separate facade versions.

### Facade versioning pattern

A practical pattern is to expose versioned facade classes:

```text
OrdersV1
OrdersV2
```

This allows older callers to keep using `OrdersV1` while newer callers adopt `OrdersV2`.

### Roadmap direction

The documentation points toward interface comparison and warnings at Gateway startup, caller runtime, or CI time. The goal is to detect incompatible interface drift before it causes runtime surprises.

---

## 5.9 Alpha limitations and known constraints

**Source:** `https://docs.dev.graftcode.com/documentation/how-graftcode-works/alpha-limitations-and-known-constraints`

The current Alpha release has important limitations. These constraints should be treated as design requirements when experimenting with Graftcode.

### Type support

Alpha supports public methods using:

- primitive/simple types,
- objects made of simple types,
- arrays of supported types,
- nested objects built from simple supported types.

The Alpha has restrictions around complex objects, advanced runtime-specific type behavior, inheritance, and some async wrappers.

### Async wrappers

The documentation notes that `Task`/`Promise`-style async wrapper return types are not supported as exposed return types in the current Alpha. Exposed public methods should be designed accordingly.

### Inheritance

Class inheritance is not supported in exposed interfaces in the current Alpha. The recommended approach is to expose standalone facade classes and delegate internally to inherited or polymorphic implementation code.

### Primitive wrappers and value types

Types such as dates, times, GUID-like values, colors, points, or spans may need to be passed as strings, timestamps, numbers, or simple objects. The receiver can parse or convert them internally. Future releases are expected to improve implicit pass-by-value handling.

### Stateful object behavior

Complex objects and stateful execution require caution:

- returned objects may represent remote object references,
- property access can trigger additional backend calls,
- stateful workflows may require sticky sessions or careful routing,
- stateless DTOs are usually easier and safer for Alpha use.

### Version compatibility

The Alpha does not guarantee backward compatibility across major Alpha releases. Teams should pin Gateway and package versions and refresh Grafts when upgrading.

### npm dependency note

For npm-based use, the documentation notes a manual SDK dependency may be required:

```bash
npm install javonet-nodejs-sdk
```

### Authentication limitation

In the current Alpha, JWT/API key authentication may need to be passed explicitly as method parameters rather than relying on fully supported security plugins.

Example pattern:

```csharp
public OrderResult PlaceOrder(string jwtToken, int productId, int quantity)
{
    ValidateToken(jwtToken);
    // Execute business operation
}
```

### Filtering exposed types

The documentation describes exposing selected facade types rather than every public type. A planned or evolving command pattern is:

```bash
gg --types MyNamespace.MyFacade,MyNamespace.AnotherFacade --modules yourlib.dll
```

### Portal and module discovery

The Alpha portal supports early workspace/project and registry concepts, but many dashboards, controls, collaboration features, and KPIs are not fully functional. AI-powered module discovery may find packages in ecosystems such as PyPI, npm, or NuGet, but many public libraries may fail generation because of Alpha type constraints.

### Alpha design recommendations

| Recommendation | Reason |
|---|---|
| Expose simple facade methods | Keeps generated Grafts stable and compatible. |
| Prefer stateless DTOs | Avoids remote object reference complexity. |
| Pass explicit auth parameters where needed | Plugin support is still evolving. |
| Pin versions | Alpha releases may break compatibility. |
| Use small experiments first | Helps validate runtime, package, and topology behavior. |

---

# 6. Integration patterns

## 6.1 Service-to-service integration

**Source:** `https://docs.dev.graftcode.com/documentation/integration-patterns/service-to-service-integration`

Graftcode can be used for service-to-service calls when teams want strongly typed internal integration without maintaining separate HTTP or RPC contracts.

### Pattern

```text
Service A imports Graft for Service B
  ↓
Service A calls ServiceBFacade.method(...)
  ↓
Hypertube routes the call to Service B’s Gateway
  ↓
Service B executes business logic
```

### Benefits

- Service B exposes a public facade rather than an endpoint schema.
- Service A receives a generated native package.
- Refactoring can follow package-version rules.
- Errors can be represented as language-level exceptions.
- Calls can remain strongly typed.
- Topology can change through configuration.

### Recommended shape

For ordinary service-to-service calls, stateless facade methods are usually safest:

```text
OrdersService.PlaceOrder(...)
InventoryService.Reserve(...)
PricingService.Calculate(...)
```

Stateful services can work, but require more attention to routing, lifetimes, callbacks, and load balancing.

---

## 6.2 Edge clients without APIs

**Source:** `https://docs.dev.graftcode.com/documentation/integration-patterns/edge-clients-without-apis`

Graftcode can allow browser, mobile, or desktop clients to consume backend capabilities through generated packages rather than hand-built HTTP APIs.

### Pattern

```text
Frontend app imports backend Graft
  ↓
Frontend calls typed backend method
  ↓
Graft routes through WSS/WebSocket-compatible transport
  ↓
Backend Gateway executes method
```

### Best practices

- Use coarse-grained backend facade methods.
- Avoid exposing internal domain objects directly to edge clients.
- Treat frontend-consumable methods as security-sensitive public surfaces.
- Keep payloads simple and predictable.
- Prefer stateless request-response patterns.
- Require explicit authentication and authorization.

### Why WSS matters

Browsers generally cannot open arbitrary raw TCP connections. WebSocket Secure (`wss://`) is the practical transport for browser-based edge clients, often through existing reverse proxies or ingress infrastructure.

### Risk to avoid

Do not expose internal implementation classes just because Graftcode can generate a client package. Edge-facing Grafts should be designed like public frontend APIs: intentional, minimal, authenticated, and versioned.

---

## 6.3 Internal business APIs

**Source:** `https://docs.dev.graftcode.com/documentation/integration-patterns/internal-business-apis`

Internal business APIs are a natural fit for Graftcode because consumers are known, teams can coordinate changes, and the public facade can represent actual business capabilities.

### Pattern

```text
Business facade class
  ↓
Public business methods
  ↓
Generated Grafts for internal consumers
```

### Example facade design

```text
Billing.CalculateInvoice(...)
Orders.SubmitOrder(...)
Customers.GetAccountSummary(...)
Shipping.SchedulePickup(...)
```

The facade should be stable and business-oriented, not a thin exposure of every private class.

### Benefits

- Business capabilities become directly callable.
- Internal consumers get IDE-visible typed methods.
- API documentation is partially replaced by generated package shape and Vision inspection.
- Refactoring is easier when public surfaces are intentionally small.
- Separate protocol contracts are not always required.

### Versioning guidance

Internal APIs still need disciplined versioning. If a method is widely consumed, changing its signature can break multiple teams. Versioned facade classes or package versions can reduce disruption.

---

## 6.4 MCP hosting and AI tools

**Source:** `https://docs.dev.graftcode.com/documentation/integration-patterns/mcp-hosting-and-ai-tools`

Graftcode can expose public static methods as tools for AI systems using the Model Context Protocol (MCP). This allows existing business methods to become callable by AI tools without building a separate AI-only service layer.

### Pattern

```text
Public static method
  ↓
Gateway configuration
  ↓
MCP tool description
  ↓
AI tool/client invokes method
  ↓
Hypertube executes business logic
```

### Documentation-derived behavior

The docs describe MCP as a protocol surface layered on top of the same underlying runtime execution model. The business logic does not need to be duplicated for AI tools. A method can be consumed by:

- Graft packages,
- edge clients,
- service-to-service callers,
- MCP-compatible AI tools.

### Good MCP candidates

- simple static methods,
- clear input and output shapes,
- deterministic business operations,
- methods with useful comments/descriptions,
- limited side effects unless explicitly intended.

### Security

AI tool exposure should use the same security thinking as any other external or semi-external integration:

- authenticate callers,
- authorize operations,
- validate inputs,
- avoid exposing sensitive internals,
- audit high-impact actions.

---

## 6.5 Modular monoliths

**Source:** `https://docs.dev.graftcode.com/documentation/integration-patterns/modular-monoliths`

Graftcode can help teams build modular monoliths that have real boundaries without immediately paying the cost of distributed systems.

### Pattern

```text
Single deployable application
  ↓
Multiple modules with public facades
  ↓
Grafts or in-memory routing between modules
  ↓
Optional future extraction by configuration/deployment changes
```

### Why this is useful

Many systems face an “extraction cliff”: a module is written as local code, then later must become a service, requiring new APIs, clients, schemas, adapters, and deployment changes. Graftcode is designed to make that transition smoother.

### Migration path

| Stage | Topology | Caller code |
|---|---|---|
| 1 | Module runs in memory | Calls Graft/local facade |
| 2 | Module runs in another runtime | Same call shape |
| 3 | Module runs in another process | Same call shape, new config |
| 4 | Module runs remotely | Same call shape, network config |
| 5 | Module scales horizontally | Same call shape, load-balanced config |

### Benefit

Teams can delay distribution until there is a real reason to distribute, while still keeping boundaries that make future extraction easier.

---

## 6.6 Microservices without contracts

**Source:** `https://docs.dev.graftcode.com/documentation/integration-patterns/microservices-without-contracts`

This pattern uses public code interfaces as the service contract instead of maintaining separate OpenAPI documents, protobuf schemas, or hand-written client SDKs.

### What “without contracts” means

It does not mean there is no contract. The contract is the public interface model:

- class names,
- method names,
- argument types,
- return types,
- exceptions,
- versioned package shape.

The difference is that the contract is generated from code rather than designed separately as a protocol document.

### Benefits

- Less schema drift between implementation and client.
- Fewer generated stubs to manage manually.
- Fewer controller/adapter layers.
- Strong typing for consumers.
- Public code surfaces become versioned package surfaces.

### When not to use this pattern

Public platform APIs may still need explicit contracts, documentation, and governance. If external consumers expect OpenAPI, protobuf, or GraphQL, those may remain the right choice.

Graftcode is strongest for internal systems where producers and consumers can use generated packages and coordinate versioning.

---

## 6.7 Event-driven communication preview

**Source:** `https://docs.dev.graftcode.com/documentation/integration-patterns/event-driven-communication-preview`

The documentation describes event-driven communication as a preview area. The key idea is that asynchronous delivery can be treated as a routing/transport concern rather than a completely different programming model.

### Conceptual pattern

```text
Caller invokes method or event-like operation
  ↓
Invocation intent enters transport plugin
  ↓
Plugin routes through queue/topic/broker
  ↓
Receiver handles invocation when delivered
```

### Possible uses

- fire-and-forget operations,
- delayed execution,
- fan-out to multiple subscribers,
- queue-backed processing,
- broker-based delivery,
- transactional event systems,
- eventually consistent workflows.

### Current status

This area is marked as preview. Teams should treat it as evolving and validate current plugin support, delivery semantics, retry behavior, ordering, and failure handling before relying on it in production.

---

# 7. Security and trust

## 7.1 Security model overview

**Source:** `https://docs.dev.graftcode.com/documentation/security-and-trust/security-model-overview`

Graftcode’s security model is based on a clear separation between metadata services and runtime execution.

The cloud helps with interface metadata and package generation. It is not intended to proxy production calls, execute business logic, or inspect runtime payloads.

### Trusted runtime components

| Component | Trust role |
|---|---|
| Application code | Owns business logic and authorization decisions. |
| Gateway | Hosts modules, exposes public interfaces, receives invocation intent. |
| Hypertube | Carries and executes invocation intent. |
| Loaded runtimes | Execute the actual code. |
| Configured plugins | Add authentication, authorization, transport, or routing behavior. |
| Customer network/infrastructure | Controls deployment, TLS, isolation, ingress, and policy. |

### Cloud-side role

The cloud/registry side is used for:

- storing public interface metadata,
- generating packages,
- serving package-manager requests,
- showing project/registry information,
- optionally aggregating high-level usage or version data.

It is not the runtime execution engine for customer business logic.

### Data boundary

Normal Graft generation does not require sending:

- source code,
- compiled modules,
- private logic,
- arguments,
- return values,
- exceptions,
- secrets,
- environment variables,
- live production calls.

### Production implication

If the cloud registry is unavailable, existing production calls should continue as long as the already-installed Grafts, Gateways, Hypertube routes, and infrastructure are running. New package generation or package retrieval may be affected.

---

## 7.2 Authentication and authorization

**Source:** `https://docs.dev.graftcode.com/documentation/security-and-trust/authentication-and-authorization`

Authentication and authorization are explicit responsibilities. Graftcode does not assume that a generated Graft should automatically be trusted.

### Authentication

Authentication can be handled through plugins or explicit method parameters, depending on release support and deployment model.

A caller-side plugin can attach credentials or identity context to invocation intent. A receiver-side plugin can validate that identity before executing the target method.

Credential types may include:

- JWTs,
- API keys,
- service credentials,
- custom tokens,
- enterprise identity context.

### Authorization

Authorization remains an application decision. The receiver must decide whether an authenticated caller can perform a specific operation.

Authorization can be implemented through:

- checks inside public methods,
- centralized policy components,
- attributes or annotations,
- role/claim checks,
- plugin-based enforcement around invocation intent.

### Failure behavior

If authentication or authorization fails, the call should fail before business logic executes. The caller receives an error/exception according to runtime mapping.

### Alpha note

The Alpha documentation indicates that fully supported JWT plugin behavior is still evolving, and explicit token parameters may be necessary in practical Alpha code.

---

## 7.3 Security plugins

**Source:** `https://docs.dev.graftcode.com/documentation/security-and-trust/security-plugins`

Security plugins allow teams to attach policy behavior around invocation intent without rewriting business logic.

Plugins operate around the call. They do not need to become part of the receiver’s core business implementation.

### Plugin categories

| Plugin type | Purpose |
|---|---|
| Authentication | Attach or validate identity. |
| Authorization | Enforce whether a caller can execute an operation. |
| Transport security | Ensure calls use required protected channels. |
| Routing | Direct calls through approved paths. |
| Audit | Record call metadata for compliance or investigation. |
| Enterprise integration | Connect with identity providers, service meshes, gateways, or brokers. |

### Example: JWT-style flow

```text
Caller invokes Graft method
  ↓
Caller-side plugin attaches token/identity context
  ↓
Invocation intent travels through Hypertube
  ↓
Receiver-side plugin validates token
  ↓
Authorization policy checks operation access
  ↓
Business method executes only if allowed
```

### Design principle

Security plugins should be visible, auditable, and composable. A team should know which plugins are configured and where enforcement occurs.

---

## 7.4 Transport security: TLS/WSS

**Source:** `https://docs.dev.graftcode.com/documentation/security-and-trust/transport-security-tls-wss`

Graftcode relies on standard transport-security mechanisms rather than a custom cryptographic system.

### Transport options

| Transport | Security model |
|---|---|
| TCP/IP | Can be protected with TLS where configured. |
| WebSocket | Should use WSS for encrypted browser/proxy-compatible traffic. |
| In-memory | Does not cross a network boundary. |
| Broker/plugin transport | Security depends on the configured broker, credentials, TLS, and policy. |

### Browser clients

Browser-based clients generally require WebSocket-compatible transports. Secure browser deployments should use `wss://` through trusted certificates and existing ingress or reverse-proxy infrastructure.

### Certificates

Certificate issuance, rotation, trust roots, and TLS policy are handled by the deployment environment. Graftcode does not replace normal certificate management.

### Security layering

Transport encryption protects data in transit. It does not replace authentication, authorization, input validation, or business-level access control.

---

## 7.5 Network boundaries and isolation

**Source:** `https://docs.dev.graftcode.com/documentation/security-and-trust/network-boundaries-and-isolation`

Graftcode is designed so runtime execution remains inside the customer’s deployed environment. Gateways are explicit entry points; they do not imply uncontrolled peer discovery or hidden lateral movement.

### Boundary model

```text
Caller network zone
  ↓ allowed route
Gateway / receiver network zone
  ↓
Loaded runtime and business logic
```

### Isolation principles

- Each service can run its own Gateway and Hypertube environment.
- Network policy controls who can reach a Gateway.
- Process and runtime boundaries remain meaningful.
- No automatic global access is granted just because a Graft exists.
- Production execution can operate in restricted outbound-network environments if package/runtime dependencies are already available.

### Zero-trust compatibility

Graftcode can be deployed in a zero-trust style: authenticate every caller, authorize every operation, encrypt transport, restrict network routes, and audit important activity.

---

## 7.6 Enterprise self-hosted engine

**Source:** `https://docs.dev.graftcode.com/documentation/security-and-trust/enterprise-self-hosted-engine`

For organizations with strict compliance, data residency, or network-control requirements, the documentation describes an enterprise self-hosted engine.

### What self-hosting includes

A self-hosted deployment can bring cloud-like metadata and package-generation functions into the customer’s own environment:

- registry services,
- UGM metadata storage,
- package generation,
- package serving,
- audit/logging around generation,
- internal project/workspace controls.

### What self-hosting does not change

Self-hosting does not change the runtime execution model. Calls still execute through Grafts, Hypertube, Gateways, and the customer’s infrastructure.

It also does not turn the self-hosted engine into a business-logic execution proxy.

### When it is useful

Self-hosted engine deployments are most relevant for:

- regulated industries,
- restricted outbound internet environments,
- strict data residency requirements,
- internal marketplace models,
- audit-heavy organizations,
- enterprises that need private package-generation infrastructure.

### Operational responsibilities

A self-hosted engine shifts more responsibility to the customer, including backups, scaling, upgrades, access control, monitoring, and internal governance.

---

# 8. Performance and efficiency

## 8.1 Compare Performance

**Source:** `https://docs.dev.graftcode.com/documentation/performance-and-efficiency/compare-performance`

The documentation includes a performance comparison area for evaluating Graftcode against REST and gRPC-style calls.

### What is compared

The comparison focuses on repeated service calls, measuring factors such as:

- end-to-end call latency,
- CPU usage,
- memory pressure,
- network overhead,
- cloud cost implications,
- performance differences across REST, gRPC, and Graftcode.

The docs describe a test style using many repeated calls, for example comparing REST `/price`, gRPC `GetPrice`, and a Graftcode method call.

### Example cloud-cost claim from docs

The documentation presents an example involving high request volume and an Azure D16s_v5-style environment where a 4.04 ms per-call saving versus REST at 5,000 requests per second is projected to reduce annual cost substantially. Treat this as a documentation example rather than a universal guarantee; actual savings depend on workload, cloud pricing, architecture, and bottlenecks.

### How to use performance claims

Performance comparisons are most useful when teams test their own workloads. Graftcode may reduce protocol, serialization, and framework overhead, but database latency, external APIs, network distance, cold starts, and business computation may dominate in real applications.

---

## 8.2 Why runtime-level integration is faster

**Source:** `https://docs.dev.graftcode.com/documentation/performance-and-efficiency/why-runtime-level-integration-is-faster`

Traditional integration often runs above the runtime. A method call is converted into a protocol request, passed through framework layers, parsed, routed, deserialized, mapped to business objects, executed, serialized again, and returned.

Graftcode attempts to reduce these layers by keeping the call closer to runtime method invocation.

### Traditional path

```text
Caller object
  ↓
Client SDK / HTTP or RPC layer
  ↓
Serialization
  ↓
Network protocol
  ↓
Server framework
  ↓
Routing/controller
  ↓
DTO mapping
  ↓
Business method
```

### Graftcode-oriented path

```text
Caller object
  ↓
Generated Graft
  ↓
Invocation intent
  ↓
Hypertube
  ↓
Receiver method
```

### Sources of potential speedup

| Source | Explanation |
|---|---|
| Fewer framework layers | Less controller/handler/routing overhead. |
| Less manual mapping | Public method shape is already the integration surface. |
| Binary invocation intent | Avoids verbose text serialization in many cases. |
| Runtime-aware execution | Calls are closer to native method dispatch. |
| In-memory mode | Can avoid network transport entirely. |
| Object/reference awareness | Can preserve richer runtime semantics where supported. |

### Caution

Runtime-level integration cannot remove physical network latency or slow business logic. It mainly reduces integration overhead around the call.

---

## 8.3 REST vs. gRPC vs. Graftcode

**Source:** `https://docs.dev.graftcode.com/documentation/performance-and-efficiency/rest-vs-grpc-vs-graftcode`

REST, gRPC, and Graftcode solve overlapping but different problems.

### Comparison

| Dimension | REST | gRPC | Graftcode |
|---|---|---|---|
| Contract style | HTTP resources/endpoints, often OpenAPI | Protobuf service definitions | Public runtime interface model |
| Developer call style | HTTP client or generated SDK | Generated stub method | Native Graft method |
| Payload format | Often JSON | Protobuf | Invocation intent / runtime-oriented binary representation |
| Browser friendliness | High | Limited without special support | Uses WebSocket/WSS for browser-style clients |
| Public API suitability | Very strong | Strong for controlled clients | Stronger for internal/generated-package consumers |
| Internal service calls | Common | Common | Primary target |
| Schema maintenance | OpenAPI/manual/generated | Protobuf | Derived from public code interface |
| Runtime semantics | Protocol-first | Protocol-first RPC | Runtime-call-first |

### When REST still makes sense

REST remains excellent for broad public APIs, resource-oriented systems, caching through HTTP infrastructure, third-party developers, and ecosystems where HTTP/JSON is the expected contract.

### When gRPC still makes sense

gRPC remains strong when explicit protobuf contracts, streaming, mature RPC tooling, and cross-language generated stubs are a good organizational fit.

### When Graftcode is distinctive

Graftcode is distinctive when the team wants public code interfaces to be the integration contract and wants generated native packages without maintaining separate schemas.

---

## 8.4 CPU, memory, and network usage

**Source:** `https://docs.dev.graftcode.com/documentation/performance-and-efficiency/cpu-memory-and-network-usage`

The documentation argues that Graftcode can reduce CPU, memory, and network overhead by removing layers and using a more direct invocation model.

### CPU

REST often spends CPU on routing, middleware, JSON parsing, serialization, and DTO mapping. gRPC reduces some overhead through binary protobuf, but still has protocol and stub machinery. Graftcode attempts to reduce CPU by keeping the call closer to runtime execution.

### Memory

REST systems may allocate intermediate strings, parsed JSON objects, DTOs, framework request/response objects, and mapping objects. gRPC may allocate protobuf buffers and generated message objects. Graftcode aims to reduce intermediate allocations by preserving method-call structure.

### Network

REST/JSON can be verbose. gRPC is compact because protobuf is binary. Graftcode’s invocation-intent representation is intended to be compact and method-focused. Actual network savings depend on payload shape, topology, compression, batching, and workload.

### Summary

| Resource | Main Graftcode advantage claimed by docs |
|---|---|
| CPU | Fewer integration layers and less conversion. |
| Memory | Fewer intermediate objects and buffers. |
| Network | Compact method-intent representation. |
| Latency | Reduced overhead around each call. |

---

## 8.5 Cloud cost implications

**Source:** `https://docs.dev.graftcode.com/documentation/performance-and-efficiency/cloud-cost-implications`

Performance overhead becomes cost when it forces additional instances, larger machines, higher CPU usage, more memory, or more network transfer.

### How Graftcode may reduce cost

- Lower CPU per call can reduce autoscaling pressure.
- Lower memory pressure can allow smaller instance sizes.
- Lower network overhead can reduce bandwidth costs.
- Fewer support components can simplify infrastructure.
- Lower latency can improve throughput per instance.

### Where savings are most likely

Savings are most visible in systems with:

- high internal request volume,
- many synchronous service-to-service calls,
- CPU-bound integration overhead,
- memory-heavy serialization layers,
- expensive cross-region traffic,
- autoscaling driven by request overhead.

### Where savings may be negligible

Savings may be small when:

- traffic is low,
- database calls dominate latency,
- external APIs dominate latency,
- systems are already overprovisioned,
- batch workloads are not call-overhead-sensitive,
- the current API layer is not a bottleneck.

---

## 8.6 When performance gains matter

**Source:** `https://docs.dev.graftcode.com/documentation/performance-and-efficiency/when-performance-gains-matter`

The docs frame performance as optional leverage, not the only reason to use Graftcode.

### Performance gains matter when

- there are many internal calls per user request,
- synchronous chains amplify latency,
- CPU or memory limits drive autoscaling,
- internal API overhead is measurable,
- services communicate at high frequency,
- latency-sensitive user experiences depend on backend response time,
- cloud cost is tied to integration overhead.

### Performance gains matter less when

- the application is low traffic,
- calls are dominated by database latency,
- calls are dominated by third-party APIs,
- batch jobs run infrequently,
- the current integration layer is not a bottleneck,
- organizational simplicity matters more than micro-optimizing calls.

### Practical advice

Use Graftcode first for integration simplicity and architectural flexibility. Measure performance on real workloads before making cost or latency commitments.

---

# 9. Quick reference

**Source:** `https://docs.dev.graftcode.com/documentation/reference/quick-reference`

This section collects the practical snippets and command patterns from the documentation.

## Start a Gateway

```bash
gg.exe --runtime <your_runtime> --modules <your_backend_library>
```

## Install a Graft package with npm

```bash
npm install @graft/nuget-EnergyPrice --registry=http://grft.dev/<project-id>__graftcode
```

## Basic usage

```js
import { EnergyService } from "@graft/nuget-EnergyPrice";

const energy = new EnergyService();
const price = await energy.getCurrentPrice("DE");
```

## Configure a host

```js
import { GraftConfig } from "@graft/nuget-EnergyPrice";

GraftConfig.host = "tcp://energy-service:9000";
```

## Configure with connection-style settings

```js
GraftConfig.setConfig(
  "name=@graft/nuget-EnergyPrice;runtime=netcore;host=ws://localhost:8004/ws"
);
```

## Frontend-to-backend example

```js
import { BackendService } from "@graft/nuget-Backend";

const backend = new BackendService();
const data = await backend.getData();
```

## Error handling

```js
try {
  const result = await service.method(params);
} catch (error) {
  // Exceptions are propagated from the target runtime according to mapping rules.
}
```

## Unit testing with a real generated service

```js
const service = new EnergyService();
const price = await service.getCurrentPrice("DE");

expect(price).toBeDefined();
```

## Mocking a Graft in tests

```js
jest.mock("@graft/nuget-EnergyPrice", () => ({
  EnergyService: jest.fn().mockImplementation(() => ({
    getCurrentPrice: jest.fn().mockResolvedValue(0.32),
  })),
}));
```

## Troubleshooting

| Symptom | Check |
|---|---|
| Gateway will not start | Verify port availability, runtime path, module path, and permissions. |
| Connection failed | Verify `GraftConfig.host`, transport type, proxy, firewall, and Gateway availability. |
| Type errors | Regenerate or update the Graft package after interface changes. |
| Method not found | Confirm the target method is public and included in the exposed facade/interface model. |
| Browser client cannot connect | Use WebSocket/WSS-compatible routing and check proxy settings. |
| Stateful call goes to wrong instance | Configure sticky sessions, connection affinity, or state-aware routing. |
| Auth not enforced | Confirm plugin configuration or explicit token validation in method code. |

---

# 10. Practical adoption checklist

Use this checklist to evaluate a first Graftcode experiment.

## Choose the first module

Pick a module that is:

- internally consumed,
- not too large,
- represented by simple public methods,
- useful enough to prove value,
- low-risk enough for an Alpha experiment.

## Design a facade

Create a narrow public facade rather than exposing internal implementation classes.

Good facade properties:

- business-oriented method names,
- simple argument and return types,
- minimal statefulness,
- explicit authentication inputs if needed,
- clear versioning expectations.

## Start locally

Begin with local or in-memory execution before moving to remote deployment.

```text
local module → Gateway → generated Graft → local caller
```

## Generate and install the Graft

Use the registry/package-manager workflow shown by Vision or the docs. Pin versions during Alpha experimentation.

## Configure routing

Use explicit configuration for the first test. Keep host, runtime, and transport settings visible in code or environment configuration.

## Add tests

Test both:

- direct method behavior in the receiver,
- caller behavior through the generated Graft.

## Add security

For Alpha use, consider passing tokens explicitly and validating inside the exposed method. As plugin support matures, move security enforcement into configured plugins where appropriate.

## Observe calls

Enable logs, tracing, correlation IDs, or OpenTelemetry-compatible context propagation where available. Verify that calls are visible across boundaries.

## Scale carefully

Use stateless methods first. Introduce stateful objects only after deciding how routing, sticky sessions, object lifetimes, and failures will be handled.

## Version public interfaces

Treat public methods like library APIs. Use versioned facades for breaking changes.

---

# 11. Glossary

| Term | Meaning |
|---|---|
| **Graft** | A generated native client package that lets a caller consume another module’s public interface. |
| **Gateway** | Runtime host that loads modules, inspects public interfaces, builds metadata, and hosts Hypertube execution. |
| **Hypertube** | Runtime bridge that carries invocation intent between caller and receiver. |
| **Vision** | Developer tool for inspecting exposed public methods, types, package commands, and examples. |
| **UGM** | Unified Graft Model: structured representation of exposed public interface metadata. |
| **IIP** | Intention Invocation Protocol: binary representation of method-call intent. |
| **Caller** | The side that invokes a method. |
| **Receiver** | The side that executes a method. |
| **Public interface** | Public classes, methods, signatures, argument types, return types, overloads, and exposed type structures. |
| **Business logic** | Private implementation behind public methods. |
| **Facade** | A deliberately designed public class or surface that exposes useful operations while hiding internals. |
| **In-memory execution** | Calls resolved without crossing a network boundary. |
| **Remote execution** | Calls routed over TCP/IP, WebSocket, WSS, or plugin transport to another process/host. |
| **Stateful call** | A call pattern involving object identity, lifetimes, sessions, callbacks, or remote references. |
| **Stateless call** | A call that depends only on its arguments and does not require object/session affinity. |
| **Transport plugin** | Extension point for routing invocation intent through custom transports, queues, brokers, or policies. |
| **Security plugin** | Extension point for authentication, authorization, identity propagation, audit, or related enforcement. |

---

## Final notes

Graftcode is best understood as a way to make integration feel more like normal programming while still respecting distributed-system boundaries. Its largest practical value is likely in internal systems where teams control both producer and consumer, can design intentional facades, and want to reduce the amount of separate API contract and client-library work.

For Alpha use, keep the first experiment simple: expose stateless methods with simple types, generate one Graft, configure one route, test locally, and only then move toward remote execution, plugins, security hardening, and scaling.
