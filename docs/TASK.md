# Senior Python Developer Tech Task – Pricing & Order Services with Graftcode

## Welcome

Welcome to the next stage of the recruitment process.

The goal of this task is to build a small but well-structured backend-oriented solution that demonstrates your Python skills, software design, ability to reason about service boundaries, and openness to developer tooling.

We value clean, maintainable code and good engineering decisions more than completing every possible feature.

---

# Objective

Build two small Python services:

1. **Pricing Service**
2. **Order Service**

The **Order Service** should use the **Pricing Service through Graftcode** and expose the order flow through **Graftcode Vision**, so that it can be tested through the generated API view.

---

# Graftcode Portal Setup

Before starting the integration part of the task, please create an account at:

https://portal.graftcode.com

After creating the account:

1. Create your own workspace/project.
2. Use flow with Create New Service.
3. Use your `ProjectKey` while configuring your Gateway and services.

The `ProjectKey` is required for:

* Gateway registration,
* Vision integration,
* service discovery and communication.

Please include short setup instructions in your `README.md`, including where the `ProjectKey` should be configured in your solution.

If you encounter issues during setup or registration, feel free to contact us by email.

---

# Business Scenario

A user wants to place an order for a product.

The system should:

1. receive an order request,
2. validate the product and quantity,
3. calculate price, discount and final amount,
4. create an order result,
5. expose the order operation so it can be tested.

---

# Services

## 1. Pricing Service – Python

The Pricing Service is responsible for calculating pricing information.

It should expose a method such as:

```python
calculate_price(product_id: str, quantity: int, customer_type: str) -> PricingResult
```

The service should:

* validate if the product exists,
* validate quantity,
* calculate base price,
* apply discount rules,
* return final price details.

Example products:

```json
[
  { "id": "laptop", "name": "Laptop", "price": 5000 },
  { "id": "mouse", "name": "Mouse", "price": 150 },
  { "id": "keyboard", "name": "Keyboard", "price": 300 }
]
```

Example discount rules:

* `regular` customer: no discount
* `premium` customer: 10% discount
* quantity >= 10: additional 5% discount

The result may include fields similar to:

```python
class PricingResult:
    product_id: str
    unit_price: float
    quantity: int
    discount_percent: float
    total_price: float
```

The example above is intentionally simplified. Improve types and modeling where you think it makes sense, especially for money calculations.

---

## 2. Order Service – Python

The Order Service is responsible for accepting an order request and producing an order result.

It should call the **Pricing Service through Graftcode**.

It should expose a method such as:

```python
place_order(product_id: str, quantity: int, customer_type: str) -> OrderResult
```

The result may include fields similar to:

```python
class OrderResult:
    order_id: str
    product_id: str
    quantity: int
    customer_type: str
    total_price: float
    status: str
```

The example above is intentionally simplified. Improve types and modeling where you think it makes sense.

The `order_id` can be generated in any reasonable way.

No database is required. In-memory storage is enough.

---

# Graftcode Requirement

The key part of this task is to connect the services using **Graftcode**, following the idea from Graftcode Academy:

> expose public methods through Graftcode Gateway, install/use a generated Graft, and call remote methods as if they were local code.

Expected flow:

```text
Pricing Service
  exposes public pricing methods through Graftcode Gateway

Order Service
  uses generated Graftcode client / Graft
  calls Pricing Service methods like local Python code

Graftcode Vision
  exposes Order Service so the place_order flow can be tested visually
```

Please do not implement this communication as a regular REST/gRPC integration between Order Service and Pricing Service. The goal is to demonstrate that you understand the Graftcode model: public methods, Gateway, generated Graft, strongly typed/local-like usage and Vision-based testing.

The solution should be runnable locally, preferably with Docker / Docker Compose.

---

# Additional Requirements

## Local vs Remote Mode

The Order Service should support two execution modes:

1. **LOCAL mode**

   * Pricing logic is executed directly in-process.
   * This simulates a modular monolith setup.

2. **REMOTE mode**

   * Pricing logic is executed through **Graftcode Gateway** using generated Grafts.
   * This simulates a distributed microservices setup.

Switching between modes should be possible through configuration only, without changing business logic in the Order Service.

One of the goals of this task is to demonstrate how the same application flow can work both as:

* modular monolith,
* distributed microservices architecture,

while keeping the Order Service code as stable as possible.

---

## Configurable Pricing Rules

Pricing rules should not be hardcoded directly inside the main calculation flow.

Please make them configurable or at least clearly isolated, so that new rules can be added without rewriting the entire calculation logic.

Example rules:

* `regular` customer: no discount
* `premium` customer: 10% discount
* quantity >= 10: additional 5% discount
* maximum total discount should not exceed 20%

You may choose your own structure, for example:

* JSON config,
* YAML config,
* Python configuration object,
* simple rule classes / strategy pattern.

Please explain your decision in the README.

---

## Partial Failure Handling

Assume that the Pricing Service may sometimes fail or be temporarily unavailable.

The Order Service should handle Pricing Service errors gracefully.

At minimum, consider:

* clear error response,
* no invalid order should be saved,
* meaningful logging,
* readable error message for the caller.

Bonus points for:

* retry strategy,
* timeout handling,
* fallback behavior,
* clear distinction between validation errors and infrastructure/service errors.

---

## Versioning / Compatibility

Assume that the Pricing Service API may evolve over time.

Please briefly explain in the README how you would approach versioning or backward compatibility of public methods exposed through Graftcode.

You do not need to implement full versioning, but we want to understand how you think about:

* changing method signatures,
* adding new fields,
* keeping existing consumers working,
* avoiding breaking changes.

---

## Edge Cases

Some business rules are intentionally not fully specified.

Please make reasonable decisions and explain them briefly in the README.

Examples:

* how discounts should combine,
* how rounding should work,
* whether prices should use `float` or `Decimal`,
* what happens for quantity `0`,
* what happens for unsupported customer types,
* what happens if product data is missing or malformed.

We are interested not only in the final implementation, but also in your reasoning.

---

# Graftcode Alpha Note

Please note that Graftcode is currently in an **alpha stage** and some instability, unclear error messages or unexpected integration issues may occur during setup.

Part of this task is also evaluating how you approach:

* working with new developer tooling,
* debugging integration problems,
* reading documentation,
* and troubleshooting independently.

If you encounter issues:

* please read the available documentation carefully,
* especially the Quick Start and Gateway/Vision sections,
* and feel free to contact us by email with technical questions or problems you encounter during the setup process.

Useful resources:

* https://graftcode.com
* https://academy.graftcode.com/quick-start

We do not expect perfection or production-grade setup. We are more interested in:

* your reasoning process,
* debugging approach,
* ability to adapt,
* and how you work with unfamiliar tooling.

---

# Important Engineering Notes

The task is intentionally small, but we expect you to think critically.

Things we will pay attention to:

* whether the Order Service really uses Pricing Service through Graftcode, not through a hand-written REST client,
* whether the public methods exposed through Graftcode have clean signatures and meaningful input/output models,
* whether the service boundary is clear and Pricing logic is not duplicated in Order Service,
* whether the solution can be tested through Graftcode Vision,
* whether you explain trade-offs and limitations in README.

AI tools are allowed, but we expect you to verify the generated code, understand the Graftcode integration model, and be able to explain why your solution does not use a traditional REST/gRPC service call between Order Service and Pricing Service.

The provided examples and snippets are intentionally simplified and may contain omissions or implementation details that should be improved in a production-ready solution.

---

# Technical Requirements

Use:

* Python
* Graftcode
* Docker / Docker Compose if needed
* simple, clean project structure

You may choose any lightweight Python framework or no framework at all, depending on what works best with your solution.

---

# What We Expect

We will look at:

* clean Python code,
* clear service boundaries,
* correct usage of Graftcode,
* good error handling,
* readable structure,
* ability to explain decisions,
* ability to improve the solution during discussion.

---

# Error Handling

Handle at least these cases:

* unknown product,
* invalid quantity,
* unsupported customer type,
* Pricing Service error.

You can decide how errors are represented.

---

# Tests

Add a few meaningful tests.

At minimum:

* price calculation test,
* discount calculation test,
* invalid product test,
* order creation test.

---

# README

Please include a `README.md` with:

* how to run the solution,
* how to test it,
* how Graftcode is used,
* how to access/test the Order Service through Vision,
* short explanation of main technical decisions.

---

# Bonus Points

Optional but welcome:

* Docker Compose setup running both services locally,
* showing the same Pricing Service callable locally and remotely by configuration,
* async implementation where it makes sense,
* structured logging,
* Decimal-based money calculations instead of float,
* additional method for retrieving created orders,
* short explanation of how this could evolve from modular monolith to microservices using Graftcode.

---

# Follow-up Discussion

During the technical interview we may ask you to:

* walk us through the solution,
* explain the Graftcode integration,
* discuss trade-offs,
* suggest improvements,
* implement a small change live.

---

# Notes

Please keep the solution small and focused.

A simple, working and well-structured solution is better than an over-engineered one.

The goal is not to build a complete commerce system, but to show how you design and implement a small service-oriented Python solution using Graftcode.
