# Cosmic Toolkit
<a href="https://github.com/RonquilloAeon/migri/actions" target="_blank">
    <img src="https://github.com/fsgsmartbuildings/cosmic-toolkit/workflows/Tests/badge.svg" alt="Tests workflow status">
</a>

**Cosmic Toolkit is an opinionated toolkit to speed up the development of complex apps.**

There aren't many examples of how to implement Domain-Driven Design in Python so this
package aims to make DDD adoption in Python applications simple and straightfoward.

This toolkit is inspired by [Cosmic Python](https://www.cosmicpython.com/). **Cosmic
Python** and Domain-Driven Design help to decouple business logic from application
concerns.

It's highly recommended that you read the [Cosmic Python](https://www.cosmicpython.com/)
book and view the sample [repository](https://github.com/cosmicpython/code/tree/chapter_13_dependency_injection).
In particular, the branch with the code for Chapter 13 is relevant for how to implement
these patterns.

**Currently in Alpha, so proceed with caution!** I'm learning DDD as I use
this package in my own projects. While this package is in Alpha, expect many breaking
changes.

## Installation
`pip install cosmic-toolkit`

## Example usage

There's a fairly complete example of how to use this package in
`./test/test_message_bus.py`.

You can also see a thorough domain model example with an aggregate root in
`./test/test_models.py`.

When you're using DDD principles, it's recommended that you start by building out your
domain models. This is where your business logic needs to reside. Thus, the domain
models can be written w/out specific knowledge of your application and domain models
should not depend on any application concerns.
