import { CuratedRoadmap } from "./types";

export const pythonRoadmap: CuratedRoadmap = {
  id: "python-programming",
  slug: "python",
  title: "Python",
  tagline: "From language idioms and OOP to generators, decorators, virtual environments, and production backend code.",
  description:
    "A comprehensive track starting with core syntax and data structures, moving through object-oriented design, context managers, iterators/generators, decorators, package management, and testing with pytest.",
  category: "Languages",
  difficulty: "Beginner",
  estimatedDuration: "6 - 8 weeks",
  badgeColor: "#3776ab",
  phases: [
    {
      id: "py-phase-1",
      order: 1,
      title: "Phase 1: Python Idioms, Types & Core Control Flow",
      description: "Dynamic typing, strings, formatted f-strings, conditionals, loops, and comprehensions.",
      topics: [
        {
          id: "py-basics-types",
          title: "Python Data Model, Dynamic Typing & Mutable vs Immutable",
          shortDescription:
            "Understand that everything in Python is an object, with identity (id), type (type), and value. Differentiate mutable and immutable types.",
          learningObjectives: [
            "Understand memory references, reference counts, and the is vs == comparison operators",
            "Differentiate immutable types (int, float, str, tuple) from mutable types (list, dict, set)",
            "Master modern f-string interpolation and type hinting annotations",
          ],
          prerequisites: ["None"],
          isEssential: true,
          resources: [
            {
              title: "Python Official Tutorial - An Informal Introduction",
              url: "https://docs.python.org/3/tutorial/introduction.html",
              publisher: "Python Software Foundation",
              type: "documentation",
              isFree: true,
            },
            {
              title: "Real Python - Python 3 Language Basics",
              url: "https://realpython.com/python-basics/",
              publisher: "Real Python",
              type: "article",
              isFree: true,
            },
          ],
        },
        {
          id: "py-data-structures",
          title: "Lists, Dictionaries, Sets, Tuples & Comprehensions",
          shortDescription:
            "Core collection types, slicing syntax, hash maps (dict), uniqueness sets, and idiomatic comprehension expressions.",
          learningObjectives: [
            "Perform advanced slicing [start:stop:step] on sequences",
            "Use dictionary methods (.get(), .setdefault(), .items(), dict comprehensions)",
            "Perform set algebra (union, intersection, symmetric difference)",
          ],
          prerequisites: ["py-basics-types"],
          isEssential: true,
          resources: [
            {
              title: "Python Official Docs - Data Structures",
              url: "https://docs.python.org/3/tutorial/datastructures.html",
              publisher: "Python Software Foundation",
              type: "documentation",
              isFree: true,
            },
            {
              title: "W3Schools Python Collections",
              url: "https://www.w3schools.com/python/python_lists.asp",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "py-functions-arguments",
          title: "Functions, *args, **kwargs, Scope (LEGB) & First-Class Functions",
          shortDescription:
            "Positional, keyword-only, arbitrary argument unpacking, local/enclosing/global/built-in scope rules, and lambda closures.",
          learningObjectives: [
            "Write flexible signatures using *args and **kwargs with dictionary unpacking",
            "Understand the LEGB variable scope resolution rule and nonlocal keyword",
            "Pass functions as arguments and return them from higher-order functions",
          ],
          prerequisites: ["py-data-structures"],
          isEssential: true,
          resources: [
            {
              title: "Python Tutorial - Defining Functions",
              url: "https://docs.python.org/3/tutorial/controlflow.html#defining-functions",
              publisher: "Python Software Foundation",
              type: "documentation",
              isFree: true,
            },
            {
              title: "Real Python - Defining Your Own Python Functions",
              url: "https://realpython.com/defining-your-own-python-function/",
              publisher: "Real Python",
              type: "article",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "py-phase-2",
      order: 2,
      title: "Phase 2: Object-Oriented Python & Dunder Methods",
      description: "Classes, instances, inheritance, properties, and special dunder (magic) methods.",
      topics: [
        {
          id: "py-oop-classes",
          title: "Classes, __init__, Instance vs Class Attributes & @property",
          shortDescription:
            "Create reusable abstractions, distinguish self from cls methods, and implement getter/setter validation with @property.",
          learningObjectives: [
            "Define classes with __init__ and handle instance vs class variable bindings",
            "Use @classmethod and @staticmethod appropriately",
            "Encapsulate fields with @property and setter descriptors",
          ],
          prerequisites: ["py-functions-arguments"],
          isEssential: true,
          resources: [
            {
              title: "Python Tutorial - Classes & Instances",
              url: "https://docs.python.org/3/tutorial/classes.html",
              publisher: "Python Software Foundation",
              type: "documentation",
              isFree: true,
            },
            {
              title: "Real Python - Object-Oriented Programming in Python",
              url: "https://realpython.com/python3-object-oriented-programming/",
              publisher: "Real Python",
              type: "article",
              isFree: true,
            },
          ],
        },
        {
          id: "py-magic-dunder",
          title: "Special Dunder Methods (__str__, __repr__, __len__, __getitem__)",
          shortDescription:
            "Integrate custom classes seamlessly into Python's built-in operators, iteration protocol, and string representation.",
          learningObjectives: [
            "Implement __str__ for human-friendly output and __repr__ for unambiguous debugging",
            "Make classes indexable and iterable with __len__ and __getitem__",
            "Support mathematical operator overloading (__add__, __eq__, __lt__)",
          ],
          prerequisites: ["py-oop-classes"],
          isEssential: true,
          resources: [
            {
              title: "Python Docs - Special Method Names (Data Model)",
              url: "https://docs.python.org/3/reference/datamodel.html#special-method-names",
              publisher: "Python Software Foundation",
              type: "documentation",
              isFree: true,
            },
            {
              title: "Real Python - Python Dunder Methods Guide",
              url: "https://realpython.com/operator-function-overloading/",
              publisher: "Real Python",
              type: "article",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "py-phase-3",
      order: 3,
      title: "Phase 3: Robustness, Files & Advanced Pythonics",
      description: "Exception hierarchies, context managers, iterators, generators, and decorators.",
      topics: [
        {
          id: "py-exceptions-files",
          title: "Exceptions, Custom Errors & Context Managers (with)",
          shortDescription:
            "Structured error handling with try-except-else-finally, custom Exception subclasses, and resource-safe file I/O.",
          learningObjectives: [
            "Catch specific exceptions rather than using bare except:",
            "Create domain-specific custom exception classes",
            "Implement custom context managers using __enter__/__exit__ or contextlib.contextmanager",
          ],
          prerequisites: ["py-magic-dunder"],
          isEssential: true,
          resources: [
            {
              title: "Python Tutorial - Errors and Exceptions",
              url: "https://docs.python.org/3/tutorial/errors.html",
              publisher: "Python Software Foundation",
              type: "documentation",
              isFree: true,
            },
            {
              title: "Real Python - Context Managers and the 'with' Statement",
              url: "https://realpython.com/python-with-statement/",
              publisher: "Real Python",
              type: "article",
              isFree: true,
            },
          ],
        },
        {
          id: "py-generators-iterators",
          title: "Iterators, Generators (yield) & Memory Efficiency",
          shortDescription:
            "Streaming massive datasets without blowing memory using lazy generator functions and generator expressions.",
          learningObjectives: [
            "Understand the iterator protocol (__iter__ and __next__)",
            "Write generator functions using yield and pipeline large stream operations",
            "Leverage the itertools and collections modules (deque, Counter, defaultdict)",
          ],
          prerequisites: ["py-exceptions-files"],
          isEssential: true,
          resources: [
            {
              title: "Python Docs - Iterators and Generators",
              url: "https://docs.python.org/3/tutorial/classes.html#iterators",
              publisher: "Python Software Foundation",
              type: "documentation",
              isFree: true,
            },
            {
              title: "Real Python - How to Use Generators and yield in Python",
              url: "https://realpython.com/introduction-to-python-generators/",
              publisher: "Real Python",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "py-decorators",
          title: "Function & Class Decorators (functools.wraps)",
          shortDescription:
            "Wrap functions to add logging, timing, authentication, caching, and rate limiting with clean @decorator syntax.",
          learningObjectives: [
            "Build decorator functions that accept and preserve arbitrary arguments with *args, **kwargs",
            "Preserve function metadata and docstrings using @functools.wraps",
            "Write parameterized decorators taking configuration arguments",
          ],
          prerequisites: ["py-generators-iterators"],
          isEssential: true,
          resources: [
            {
              title: "Real Python - Primer on Python Decorators",
              url: "https://realpython.com/primer-on-python-decorators/",
              publisher: "Real Python",
              type: "article",
              isFree: true,
            },
            {
              title: "Python Docs - functools.wraps",
              url: "https://docs.python.org/3/library/functools.html#functools.wraps",
              publisher: "Python Software Foundation",
              type: "documentation",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "py-phase-4",
      order: 4,
      title: "Phase 4: Tooling, Testing & Production Ecosystem",
      description: "Virtual environments, dependency management, unit testing with pytest, and typing.",
      topics: [
        {
          id: "py-venv-packaging",
          title: "Virtual Environments, Dependency Management & pyproject.toml",
          shortDescription:
            "Isolate project dependencies using venv/pip or modern tools like uv and poetry, adhering to modern packaging standards.",
          learningObjectives: [
            "Create, activate, and manage isolated virtual environments",
            "Pin and reproduce dependencies with requirements.txt and lockfiles",
            "Structure clean multi-file Python packages with __init__.py",
          ],
          prerequisites: ["py-decorators"],
          isEssential: true,
          resources: [
            {
              title: "Python Docs - Virtual Environments and Packages",
              url: "https://docs.python.org/3/tutorial/venv.html",
              publisher: "Python Software Foundation",
              type: "documentation",
              isFree: true,
            },
            {
              title: "Python Packaging User Guide",
              url: "https://packaging.python.org/en/latest/tutorials/installing-packages/",
              publisher: "Python.org",
              type: "documentation",
              isFree: true,
            },
          ],
        },
        {
          id: "py-testing-pytest",
          title: "Unit Testing, Assertions & Fixtures with pytest",
          shortDescription:
            "Write maintainable, automated test suites with pytest, parameterized test cases, and dependency injection fixtures.",
          learningObjectives: [
            "Write clean test functions using standard assert statements",
            "Create reusable test setup and teardown logic with @pytest.fixture",
            "Run test suites with coverage reports and mocking with unittest.mock",
          ],
          prerequisites: ["py-venv-packaging"],
          isEssential: true,
          resources: [
            {
              title: "pytest Documentation - Getting Started",
              url: "https://docs.pytest.org/en/stable/getting-started.html",
              publisher: "pytest.org",
              type: "documentation",
              isFree: true,
            },
            {
              title: "Real Python - Effective Python Testing With Pytest",
              url: "https://realpython.com/pytest-python-testing/",
              publisher: "Real Python",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
      ],
    },
  ],
};

