import { CuratedRoadmap } from "./types";

export const cRoadmap: CuratedRoadmap = {
  id: "c-programming",
  slug: "c",
  title: "C Programming",
  tagline: "Master low-level systems programming, memory architectures, and the foundational language of computing.",
  description:
    "A structured, sequential curriculum taking you from standard compilation and data representations to pointer arithmetic, dynamic memory allocation, system structures, and low-level file I/O.",
  category: "Languages",
  difficulty: "Beginner",
  estimatedDuration: "8 - 10 weeks",
  badgeColor: "#3b82f6",
  phases: [
    {
      id: "c-phase-1",
      order: 1,
      title: "Phase 1: Environment, Toolchain & Core Syntax",
      description: "Set up GCC/Clang, learn the compilation pipeline, and understand fundamental types.",
      topics: [
        {
          id: "c-toolchain",
          title: "The C Compilation Pipeline (Preprocessing, Compilation, Assembly, Linking)",
          shortDescription:
            "Understand how source code (.c) translates into machine code through the preprocessor, compiler, assembler, and linker.",
          learningObjectives: [
            "Use GCC/Clang commands (-Wall, -Wextra, -O2, -g) to compile and inspect output stages",
            "Understand header inclusion (#include) and macro expansion (#define)",
            "Distinguish between compile-time syntax errors and link-time undefined references",
          ],
          prerequisites: ["Basic command-line / terminal proficiency"],
          isEssential: true,
          resources: [
            {
              title: "GNU C Manual - Compilation & Invocation",
              url: "https://www.gnu.org/software/gnu-c-manual/gnu-c-manual.html",
              publisher: "GNU Project",
              type: "documentation",
              isFree: true,
            },
            {
              title: "CS50 Introduction to C & Compilation",
              url: "https://cs50.harvard.edu/x/2024/weeks/1/",
              publisher: "Harvard CS50",
              type: "interactive",
              isFree: true,
            },
            {
              title: "GeeksforGeeks C Compilation Process",
              url: "https://www.geeksforgeeks.org/compiling-a-c-program-behind-the-scenes/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
          ],
        },
        {
          id: "c-data-types",
          title: "Primitive Data Types, Storage Sizes & Type Qualifiers",
          shortDescription:
            "Deep dive into integer representations, IEEE 754 floating-point, sign extensions, size_t, and qualifiers like const and volatile.",
          learningObjectives: [
            "Inspect sizes with sizeof for char, short, int, long, float, and double",
            "Understand signed vs unsigned overflow and bit-level representations",
            "Use fixed-width integers from <stdint.h> (int32_t, uint64_t)",
          ],
          prerequisites: ["c-toolchain"],
          isEssential: true,
          resources: [
            {
              title: "DevDocs C Reference - Types",
              url: "https://devdocs.io/c/types",
              publisher: "DevDocs",
              type: "documentation",
              isFree: true,
            },
            {
              title: "W3Schools C Data Types Guide",
              url: "https://www.w3schools.com/c/c_data_types.php",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "c-control-flow",
          title: "Operators, Expressions & Control Structures",
          shortDescription:
            "Branching and iteration constructs: if-else, switch-case, while, do-while, and for loops with break and continue.",
          learningObjectives: [
            "Implement multi-branch decision structures and nested loops",
            "Analyze operator precedence, associativity, and short-circuit evaluation",
            "Avoid common bugs like using assignment = instead of equality ==",
          ],
          prerequisites: ["c-data-types"],
          isEssential: true,
          resources: [
            {
              title: "W3Schools C Operators & Conditions",
              url: "https://www.w3schools.com/c/c_operators.php",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
            {
              title: "Programiz C Flow Control",
              url: "https://www.programiz.com/c-programming/c-decision-making",
              publisher: "Programiz",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "c-phase-2",
      order: 2,
      title: "Phase 2: Functions, Scope & Structured Memory",
      description: "Function prototypes, stack call frames, variable lifetimes, arrays, and string handling.",
      topics: [
        {
          id: "c-functions-scope",
          title: "Functions, Call Stack & Variable Lifetimes",
          shortDescription:
            "Function prototypes, pass-by-value semantics, stack frames, recursion, and storage classes (static, extern, auto).",
          learningObjectives: [
            "Write header files with prototypes and include guards",
            "Visualize the activation record on the stack during function calls",
            "Use static local variables to preserve state across invocations",
          ],
          prerequisites: ["c-control-flow"],
          isEssential: true,
          resources: [
            {
              title: "GNU C Manual - Functions & Scope",
              url: "https://www.gnu.org/software/gnu-c-manual/gnu-c-manual.html#Functions",
              publisher: "GNU Project",
              type: "documentation",
              isFree: true,
            },
            {
              title: "GeeksforGeeks Storage Classes in C",
              url: "https://www.geeksforgeeks.org/storage-classes-in-c/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
          ],
        },
        {
          id: "c-arrays-strings",
          title: "Arrays, Multidimensional Arrays & Null-Terminated Strings",
          shortDescription:
            "Contiguous memory layouts, row-major indexing, string safety, and standard library routines (<string.h>).",
          learningObjectives: [
            "Manipulate 1D and 2D arrays in contiguous memory",
            "Understand why C strings must terminate with the null byte '\\0'",
            "Use bounded string operations (strncpy, snprintf, strncat) to prevent buffer overflows",
          ],
          prerequisites: ["c-functions-scope"],
          isEssential: true,
          resources: [
            {
              title: "W3Schools C Strings & Arrays",
              url: "https://www.w3schools.com/c/c_strings.php",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
            {
              title: "DevDocs C String Library Functions",
              url: "https://devdocs.io/c/string/byte",
              publisher: "DevDocs",
              type: "documentation",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "c-phase-3",
      order: 3,
      title: "Phase 3: Pointers & Dynamic Memory Architecture",
      description: "The core superpower of C: memory addresses, indirection, pointer arithmetic, and heap allocation.",
      topics: [
        {
          id: "c-pointers-basics",
          title: "Pointer Fundamentals & Address-of Operators",
          shortDescription:
            "Direct memory addresses, dereferencing (*), address-of (&), NULL pointers, and void pointers.",
          learningObjectives: [
            "Explain how variables reside at specific byte addresses in virtual memory",
            "Implement pass-by-reference simulation using pointers in function parameters",
            "Check and prevent null pointer dereferences and uninitialized pointer traps",
          ],
          prerequisites: ["c-arrays-strings"],
          isEssential: true,
          resources: [
            {
              title: "CS50 Week 4: Memory & Pointers",
              url: "https://cs50.harvard.edu/x/2024/weeks/4/",
              publisher: "Harvard CS50",
              type: "interactive",
              isFree: true,
            },
            {
              title: "W3Schools C Pointers Guide",
              url: "https://www.w3schools.com/c/c_pointers.php",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "c-pointer-arithmetic",
          title: "Pointer Arithmetic & Array-Pointer Duality",
          shortDescription:
            "How adding integers to pointers shifts addresses by sizeof(type), pointer differences, and array decays.",
          learningObjectives: [
            "Navigate memory buffers using pointer increments *(ptr + i)",
            "Understand array name decay to a pointer to its first element",
            "Work with pointers to pointers (char** argv for command line arguments)",
          ],
          prerequisites: ["c-pointers-basics"],
          isEssential: true,
          resources: [
            {
              title: "GeeksforGeeks Pointer Arithmetic in C",
              url: "https://www.geeksforgeeks.org/pointer-arithmetics-in-c-with-examples/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
            {
              title: "DevDocs C Pointer Types & Conversions",
              url: "https://devdocs.io/c/language/pointer",
              publisher: "DevDocs",
              type: "documentation",
              isFree: true,
            },
          ],
        },
        {
          id: "c-dynamic-memory",
          title: "Dynamic Heap Allocation (malloc, calloc, realloc, free)",
          shortDescription:
            "Allocating runtime memory on the heap, checking for allocation failures, avoiding leaks, and debugging with Valgrind.",
          learningObjectives: [
            "Allocate dynamic buffers with malloc() and zeroed memory with calloc()",
            "Resize existing memory blocks safely using realloc()",
            "Free every allocated pointer and prevent double frees, dangling pointers, and memory leaks",
          ],
          prerequisites: ["c-pointer-arithmetic"],
          isEssential: true,
          resources: [
            {
              title: "DevDocs C stdlib Memory Allocation",
              url: "https://devdocs.io/c/memory",
              publisher: "DevDocs",
              type: "documentation",
              isFree: true,
            },
            {
              title: "Valgrind Quick Start Guide for Memory Leak Detection",
              url: "https://valgrind.org/docs/manual/quick-start.html",
              publisher: "Valgrind.org",
              type: "documentation",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "c-phase-4",
      order: 4,
      title: "Phase 4: Composite Data Structures & System I/O",
      description: "Custom structures, memory alignment/padding, unions, bit-fields, and file operations.",
      topics: [
        {
          id: "c-structs-unions",
          title: "Structures (struct), Typedefs & Memory Alignment",
          shortDescription:
            "Group heterogeneous data, pass structs by pointer, understand byte padding and struct layout rules.",
          learningObjectives: [
            "Define composite types using struct and clean aliases with typedef",
            "Access members through values (.) and pointer arrows (->)",
            "Identify struct padding, alignment boundaries, and memory footprint",
          ],
          prerequisites: ["c-dynamic-memory"],
          isEssential: true,
          resources: [
            {
              title: "W3Schools C Structures",
              url: "https://www.w3schools.com/c/c_structs.php",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
            {
              title: "The Lost Art of Structure Packing (Eric S. Raymond)",
              url: "http://www.catb.org/esr/structure-packing/",
              publisher: "Eric S. Raymond",
              type: "article",
              isFree: true,
            },
          ],
        },
        {
          id: "c-file-io",
          title: "File I/O & Stream Processing (fopen, fread, fwrite, fclose)",
          shortDescription:
            "Text and binary file modes, stream buffering, error checking with feof and ferror, and seek positioning.",
          learningObjectives: [
            "Open, read, write, and safely close file streams using FILE*",
            "Process structured records with binary fread() and fwrite()",
            "Navigate file offsets using fseek(), ftell(), and rewind()",
          ],
          prerequisites: ["c-structs-unions"],
          isEssential: true,
          resources: [
            {
              title: "DevDocs C File Access & Input/Output",
              url: "https://devdocs.io/c/io",
              publisher: "DevDocs",
              type: "documentation",
              isFree: true,
            },
            {
              title: "W3Schools C File Handling",
              url: "https://www.w3schools.com/c/c_files.php",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "c-function-pointers",
          title: "Function Pointers & Callback Architectures",
          shortDescription:
            "Store executable function addresses in pointer variables to build callbacks, dispatch tables, and generic algorithms.",
          learningObjectives: [
            "Declare and invoke function pointers with specific return types and parameter lists",
            "Pass custom comparator callbacks to standard library qsort()",
            "Construct event-driven handler tables",
          ],
          prerequisites: ["c-file-io"],
          isEssential: false,
          resources: [
            {
              title: "GeeksforGeeks Function Pointers in C",
              url: "https://www.geeksforgeeks.org/function-pointer-in-c/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
            {
              title: "DevDocs C qsort & Comparison Callbacks",
              url: "https://devdocs.io/c/algorithm/qsort",
              publisher: "DevDocs",
              type: "documentation",
              isFree: true,
            },
          ],
        },
      ],
    },
  ],
};

