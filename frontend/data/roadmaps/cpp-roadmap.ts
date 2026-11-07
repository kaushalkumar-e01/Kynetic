import { CuratedRoadmap } from "./types";

export const cppRoadmap: CuratedRoadmap = {
  id: "cpp-programming",
  slug: "cpp",
  title: "C++",
  tagline: "Build high-performance, deterministic systems with modern C++, RAII, generic templates, and the STL.",
  description:
    "From core OOP paradigms to Modern C++ standards (C++11 through C++20). Master value semantics, smart pointers, template metaprogramming, STL algorithms, and zero-cost abstractions.",
  category: "Languages",
  difficulty: "Intermediate",
  estimatedDuration: "10 - 12 weeks",
  badgeColor: "#00599c",
  phases: [
    {
      id: "cpp-phase-1",
      order: 1,
      title: "Phase 1: Moving from C to C++ & Modern Basics",
      description: "Namespaces, auto type deduction, references, stream I/O, and string views.",
      topics: [
        {
          id: "cpp-modern-syntax",
          title: "C++ Streams, Namespaces & Type Deduction",
          shortDescription:
            "Replace printf/scanf with std::cout/std::cin, organize code with namespaces, and deduce types with auto and decltype.",
          learningObjectives: [
            "Use std::cin, std::cout, and std::cerr with stream formatting manipulators",
            "Prevent identifier collisions using custom and nested namespaces",
            "Apply auto and const auto& for clean, type-safe declarations",
          ],
          prerequisites: ["Fundamental programming syntax"],
          isEssential: true,
          resources: [
            {
              title: "LearnCpp - Introduction to C++ Basics & Streams",
              url: "https://www.learncpp.com/cpp-tutorial/introduction-to-iostream-cout-cin-and-endl/",
              publisher: "LearnCpp",
              type: "tutorial",
              isFree: true,
            },
            {
              title: "cppreference - Fundamental Types & Auto Specifier",
              url: "https://en.cppreference.com/w/cpp/language/auto",
              publisher: "cppreference.com",
              type: "documentation",
              isFree: true,
            },
          ],
        },
        {
          id: "cpp-references-const",
          title: "References, Const Correctness & Value Semantics",
          shortDescription:
            "Lvalue references, const references for zero-copy parameters, and compile-time immutability with constexpr.",
          learningObjectives: [
            "Distinguish between pointers and references (re-seating, nullability, syntax)",
            "Pass large objects by const T& to eliminate unnecessary copies",
            "Use constexpr and consteval for compile-time constant computation",
          ],
          prerequisites: ["cpp-modern-syntax"],
          isEssential: true,
          resources: [
            {
              title: "LearnCpp - Value Categories and Lvalue References",
              url: "https://www.learncpp.com/cpp-tutorial/lvalue-references/",
              publisher: "LearnCpp",
              type: "tutorial",
              isFree: true,
            },
            {
              title: "cppreference - Reference Declaration",
              url: "https://en.cppreference.com/w/cpp/language/reference",
              publisher: "cppreference.com",
              type: "documentation",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "cpp-phase-2",
      order: 2,
      title: "Phase 2: Object-Oriented Programming & RAII",
      description: "Encapsulation, constructors, member initializer lists, rule of 3/5/0, and polymorphism.",
      topics: [
        {
          id: "cpp-classes-raii",
          title: "Classes, Constructors & RAII (Resource Acquisition Is Initialization)",
          shortDescription:
            "Tie resource lifetimes (memory, sockets, file locks) strictly to object lifetimes via constructors and destructors.",
          learningObjectives: [
            "Write member initializer lists to avoid default constructor overhead",
            "Implement RAII wrappers that guarantee automatic cleanup upon scope exit",
            "Understand access specifiers: public, private, and protected",
          ],
          prerequisites: ["cpp-references-const"],
          isEssential: true,
          resources: [
            {
              title: "cppreference - RAII Idiom",
              url: "https://en.cppreference.com/w/cpp/language/raii",
              publisher: "cppreference.com",
              type: "documentation",
              isFree: true,
            },
            {
              title: "LearnCpp - Constructors & Member Initializer Lists",
              url: "https://www.learncpp.com/cpp-tutorial/constructor-member-initializer-lists/",
              publisher: "LearnCpp",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "cpp-rule-of-five",
          title: "Copy/Move Semantics, Rvalues & The Rule of 3/5/0",
          shortDescription:
            "Move semantics (std::move, rvalue references &&), copy constructors, assignment operators, and deep copies.",
          learningObjectives: [
            "Differentiate lvalues (identity) from rvalues (temporary resources)",
            "Implement move constructor and move assignment operator for transfer of ownership",
            "Apply the Rule of Zero by preferring standard library containers",
          ],
          prerequisites: ["cpp-classes-raii"],
          isEssential: true,
          resources: [
            {
              title: "cppreference - The Rule of Three/Five/Zero",
              url: "https://en.cppreference.com/w/cpp/language/rule_of_three",
              publisher: "cppreference.com",
              type: "documentation",
              isFree: true,
            },
            {
              title: "LearnCpp - Introduction to Move Semantics & Rvalue References",
              url: "https://www.learncpp.com/cpp-tutorial/introduction-to-smart-pointers-move-semantics/",
              publisher: "LearnCpp",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "cpp-polymorphism",
          title: "Inheritance, Virtual Functions & Dynamic Dispatch (vtable)",
          shortDescription:
            "Subtyping, override, final, abstract base classes with pure virtual functions, and vtable memory overhead.",
          learningObjectives: [
            "Implement runtime polymorphism using base pointers/references and virtual methods",
            "Always declare virtual destructors on polymorphic base classes to avoid leaks",
            "Explain vptr and vtable layout and dynamic_cast mechanisms",
          ],
          prerequisites: ["cpp-rule-of-five"],
          isEssential: true,
          resources: [
            {
              title: "LearnCpp - Virtual Functions and Polymorphism",
              url: "https://www.learncpp.com/cpp-tutorial/virtual-functions/",
              publisher: "LearnCpp",
              type: "tutorial",
              isFree: true,
            },
            {
              title: "cppreference - Virtual Functions Specifier",
              url: "https://en.cppreference.com/w/cpp/language/virtual",
              publisher: "cppreference.com",
              type: "documentation",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "cpp-phase-3",
      order: 3,
      title: "Phase 3: Modern Memory Management & Smart Pointers",
      description: "Replace raw new/delete with std::unique_ptr, std::shared_ptr, and std::weak_ptr.",
      topics: [
        {
          id: "cpp-smart-pointers",
          title: "std::unique_ptr, std::shared_ptr & std::weak_ptr",
          shortDescription:
            "Zero-overhead exclusive ownership, reference-counted shared ownership, and breaking circular reference cycles.",
          learningObjectives: [
            "Use std::make_unique<T>() as the default safe dynamic allocation idiom",
            "Manage shared resources with std::make_shared<T>() and observe control blocks",
            "Break memory cycles and dangling pointers using std::weak_ptr",
          ],
          prerequisites: ["cpp-classes-raii"],
          isEssential: true,
          resources: [
            {
              title: "cppreference - Smart Pointer Utilities",
              url: "https://en.cppreference.com/w/cpp/memory/unique_ptr",
              publisher: "cppreference.com",
              type: "documentation",
              isFree: true,
            },
            {
              title: "LearnCpp - std::unique_ptr & std::shared_ptr Deep Dive",
              url: "https://www.learncpp.com/cpp-tutorial/std-unique_ptr/",
              publisher: "LearnCpp",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "cpp-phase-4",
      order: 4,
      title: "Phase 4: Standard Template Library (STL) & Generic Programming",
      description: "Containers, iterators, algorithms, lambda expressions, and templates.",
      topics: [
        {
          id: "cpp-stl-containers",
          title: "STL Containers (vector, deque, list, unordered_map, set)",
          shortDescription:
            "Choose the right container based on cache locality, contiguous memory, lookup speeds, and iterator invalidation.",
          learningObjectives: [
            "Master std::vector growth mechanics, capacity vs size, and emplace_back",
            "Use std::unordered_map for O(1) average hash lookups vs std::map for ordered keys",
            "Analyze iterator invalidation rules across insertion and deletion",
          ],
          prerequisites: ["cpp-smart-pointers"],
          isEssential: true,
          resources: [
            {
              title: "cppreference - Containers Library Overview",
              url: "https://en.cppreference.com/w/cpp/container",
              publisher: "cppreference.com",
              type: "documentation",
              isFree: true,
            },
            {
              title: "LearnCpp - STL Containers Overview",
              url: "https://www.learncpp.com/cpp-tutorial/stl-containers-overview/",
              publisher: "LearnCpp",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "cpp-algorithms-lambdas",
          title: "STL Algorithms, Ranges & Lambda Expressions",
          shortDescription:
            "Prefer standard algorithms (std::sort, std::find, std::transform) over raw loops, paired with concise closures.",
          learningObjectives: [
            "Write lambda expressions with capture clauses ([&], [=], [this])",
            "Chain transformations using C++20 std::ranges::views",
            "Implement custom predicates and comparator callbacks",
          ],
          prerequisites: ["cpp-stl-containers"],
          isEssential: true,
          resources: [
            {
              title: "cppreference - Algorithms Library",
              url: "https://en.cppreference.com/w/cpp/algorithm",
              publisher: "cppreference.com",
              type: "documentation",
              isFree: true,
            },
            {
              title: "LearnCpp - Introduction to Lambdas",
              url: "https://www.learncpp.com/cpp-tutorial/introduction-to-lambdas-anonymous-functions/",
              publisher: "LearnCpp",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "cpp-templates-concepts",
          title: "Function & Class Templates, Concepts (C++20)",
          shortDescription:
            "Type-agnostic generic programming, template specialization, and compile-time constraint validation with C++20 concepts.",
          learningObjectives: [
            "Write generic data structures and functions using template <typename T>",
            "Constrain template arguments using requires clauses and concepts",
            "Understand template instantiation mechanics and compiler error diagnostics",
          ],
          prerequisites: ["cpp-algorithms-lambdas"],
          isEssential: false,
          resources: [
            {
              title: "cppreference - Templates and Concepts",
              url: "https://en.cppreference.com/w/cpp/language/constraints",
              publisher: "cppreference.com",
              type: "documentation",
              isFree: true,
            },
            {
              title: "LearnCpp - Function Templates & Concepts",
              url: "https://www.learncpp.com/cpp-tutorial/function-templates/",
              publisher: "LearnCpp",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
      ],
    },
  ],
};

