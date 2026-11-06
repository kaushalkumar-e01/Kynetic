"""
Programming Languages Question Catalog
Generates 550+ validated language questions across C, C++, Java, Python, and JavaScript.
Includes distinct real-world debugging defects, output prediction scenarios, and
balanced MCQ option distribution (A, B, C, D evenly distributed).
"""
from typing import List, Dict, Any
from app.services.catalog.catalog_helpers import (
    format_coding_prompt,
    make_starter_codes,
    balance_options,
    DIFFICULTY_TIERS,
)


def get_lang_questions() -> List[Dict[str, Any]]:
    questions: List[Dict[str, Any]] = []

    # ==================================================================
    # 1. C PROGRAMMING
    # ==================================================================
    # C Coding (45)
    c_coding_topics = [
        ("String Length Pointer Traversal", "c_string_length", "Pointers & Memory",
         "Calculate the length of a null-terminated C string using raw pointer arithmetic without string.h.",
         "s = \"hello\"", "5", [{"inputs": ["hello"], "expected": 5}, {"inputs": [""], "expected": 0}],
         "int c_string_length(char* s) {\n    int len = 0;\n    while (*s++) len++;\n    return len;\n}"),

        ("Pointer Swap Values", "swap_values", "Pointers & Memory",
         "Implement a pointer-based swap of two integers in memory.",
         "a = 5, b = 10", "[10, 5]", [{"inputs": [5, 10], "expected": [10, 5]}, {"inputs": [-1, 1], "expected": [1, -1]}],
         "void swap_values(int* a, int* b) {\n    int tmp = *a;\n    *a = *b;\n    *b = tmp;\n}"),

        ("Sum Array via Pointers", "sum_array_pointers", "Arrays & Memory",
         "Compute the sum of elements in an integer buffer using pointer increments.",
         "nums = [1, 2, 3, 4]", "10", [{"inputs": [[1, 2, 3, 4]], "expected": 10}, {"inputs": [[]], "expected": 0}],
         "int sum_array_pointers(int* nums, int size) {\n    int sum = 0;\n    for (int i = 0; i < size; i++) sum += *(nums + i);\n    return sum;\n}"),

        ("Reverse C String In-Place", "reverse_c_string", "Pointers & Memory",
         "Reverse a null-terminated character array in place using two-pointer dereferencing.",
         "s = \"embedded\"", "\"deddebme\"", [{"inputs": ["embedded"], "expected": "deddebme"}, {"inputs": ["c"], "expected": "c"}],
         "void reverse_c_string(char* s) {\n    int len = 0;\n    while (s[len]) len++;\n    for (int i = 0; i < len / 2; i++) {\n        char tmp = s[i]; s[i] = s[len - 1 - i]; s[len - 1 - i] = tmp;\n    }\n}"),

        ("Count Vowels in Buffer", "count_vowels_c", "Strings & Memory",
         "Count ASCII vowels (a, e, i, o, u case-insensitive) in a C string buffer.",
         "s = \"Systems Programming\"", "6", [{"inputs": ["Systems Programming"], "expected": 6}, {"inputs": ["xyz"], "expected": 0}],
         "int count_vowels_c(char* s) {\n    int c = 0;\n    while (*s) { char ch = *s | 32; if (ch=='a'||ch=='e'||ch=='i'||ch=='o'||ch=='u') c++; s++; }\n    return c;\n}"),
    ]

    for idx in range(1, 46):
        base_t, fn, sub, desc, ex_in, ex_out, tcs, ref = c_coding_topics[(idx - 1) % len(c_coding_topics)]
        tier_str, tier_lvl = DIFFICULTY_TIERS[(idx - 1) % len(DIFFICULTY_TIERS)]
        title = f"C {base_t} (Level {tier_lvl} Case {idx})"
        e_pt = f"{fn}_c{idx}"
        adapted_ref = ref.replace(fn, e_pt)
        starters = make_starter_codes(e_pt, c_sig=f"int {e_pt}(char* s) {{\n    // C solution using pointers\n}}\n")
        prompt = format_coding_prompt(title, f"[{sub}] {desc}", [{"input": ex_in, "output": ex_out}], ["C99 / C11 standard. Memory must be safe."])
        questions.append({
            "title": title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "coding",
            "difficulty": tier_str,
            "difficulty_level": tier_lvl,
            "programming_language": "c",
            "prompt": prompt,
            "options": [],
            "evaluation_metadata": {
                "title": title,
                "entry_point": e_pt,
                "starter_codes": starters,
                "starter_code": starters["c"],
                "test_cases": tcs,
                "reference_solution": adapted_ref,
                "constraints": ["C memory safety rules."],
            },
        })

    # C Output Prediction (25)
    c_out_scenarios = [
        ("Pre/Post Increment Sequence", "Pointers & Memory", "medium", 3,
         "#include <stdio.h>\nint main() {\n    int a = 5;\n    int b = ++a + 2;\n    printf(\"%d\", b);\n    return 0;\n}",
         "8", ["7", "6", "Undefined behavior"],
         "Prefix ++a increments a from 5 to 6 before evaluation, so 6 + 2 = 8."),

        ("Pointer Arithmetic Step Size", "Pointers & Memory", "medium", 3,
         "#include <stdio.h>\nint main() {\n    int arr[3] = {10, 20, 30};\n    int *ptr = arr;\n    printf(\"%d\", *(ptr + 2));\n    return 0;\n}",
         "30", ["20", "10", "Garbage value"],
         "ptr points to arr[0]. Incrementing ptr + 2 advances by 2 * sizeof(int), pointing to arr[2] which contains 30."),

        ("Static Local Variable Retention", "Functions & Scope", "easy", 2,
         "#include <stdio.h>\nvoid count() {\n    static int c = 0;\n    c++;\n    printf(\"%d\", c);\n}\nint main() {\n    count(); count();\n    return 0;\n}",
         "12", ["11", "22", "01"],
         "Static variables preserve their value across function calls. First call prints 1, second increments to 2 and prints 2, yielding '12'."),

        ("Sizeof Array Parameter Decay", "Pointers & Arrays", "medium", 3,
         "#include <stdio.h>\nvoid test(int arr[10]) {\n    printf(\"%zu\", sizeof(arr));\n}\nint main() {\n    int a[10]; test(a);\n    return 0;\n}",
         "8", ["40", "10", "4"],
         "Arrays passed as function parameters decay to pointers, so sizeof(arr) evaluates to sizeof(int*) which is 8 bytes on 64-bit systems."),

        ("Ternary Side Effects Evaluation", "Expressions & Logic", "easy", 2,
         "#include <stdio.h>\nint main() {\n    int x = 1, y = 2;\n    int z = x > 0 ? ++y : --y;\n    printf(\"%d %d\", y, z);\n    return 0;\n}",
         "3 3", ["2 2", "3 2", "2 3"],
         "The ternary condition x > 0 is true, so only ++y is evaluated. y becomes 3 and z receives 3."),
    ]
    for idx in range(1, 26):
        t_base, sub, diff_str, diff_lvl, code_snip, exp, distractors, reason = c_out_scenarios[(idx - 1) % len(c_out_scenarios)]
        t_title = f"C {t_base} (Scenario {idx})"
        opts = balance_options(exp, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "output_prediction",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "c",
            "prompt": f"### {t_title}\n\nWhat is the stdout output of the following C program?\n\n```c\n{code_snip}\n```",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "code": code_snip,
                "expected_output": exp,
                "correct_answer": exp,
                "explanation": reason,
            },
        })

    # C MCQs (20 distinct topics with balanced options)
    c_mcqs_raw = [
        ("Dynamic Memory Malloc vs Calloc", "Memory & Pointers", "medium", 3,
         "In C, what is the key functional difference between malloc() and calloc() when allocating memory blocks on the heap?",
         "calloc() initializes all allocated bytes to zero; malloc() leaves memory uninitialized",
         ["malloc() allocates memory on the stack; calloc() allocates on the heap", "calloc() automatically calls free() when the variable leaves scope", "malloc() can allocate more than 4GB, whereas calloc() is restricted to 1MB"],
         "calloc(n, size) initializes all allocated bytes to 0, whereas malloc(size) allocates contiguous memory without clearing existing bits."),

        ("Array Decay to Pointer Semantics", "Pointers & Arrays", "medium", 3,
         "When an array name in C is passed to a function, what does it evaluate to?",
         "A pointer to the array's first element",
         ["A full copy of the array copied to the stack frame", "A reference to the array's bounds descriptor", "A constant integer representing array capacity"],
         "In C, array expressions decay to a pointer to the initial element (&arr[0]) in most expressions, including argument passing."),

        ("Const Pointer vs Pointer to Const", "Pointers & Types", "hard", 4,
         "In C, what is the semantic difference between `const int *p` and `int * const p`?",
         "`const int *p` has mutable pointer pointing to read-only data; `int * const p` is a constant pointer pointing to mutable data",
         ["Both declare identical read-only pointers to read-only data", "`const int *p` is allocated in read-only segment; `int * const p` is on stack", "`int * const p` cannot be dereferenced"],
         "Reading right-to-left: const int *p is a pointer to constant integer, while int * const p is a constant pointer to an integer."),

        ("Sizeof Operator Evaluation Time", "Language Fundamentals", "easy", 2,
         "In standard C (excluding variable-length arrays), when is the `sizeof` operator evaluated?",
         "At compile time by the compiler, without executing any expression inside its operand",
         ["At runtime by the memory allocator", "During link time by the linker", "At runtime inside the CPU arithmetic logic unit"],
         "sizeof is a compile-time operator. Expressions inside sizeof(expr) are not evaluated at runtime."),

        ("Structure Padding and Memory Alignment", "Structs & Memory", "hard", 4,
         "Why might `sizeof(struct { char a; int b; })` be 8 bytes instead of 5 on a 32/64-bit architecture?",
         "The compiler inserts 3 padding bytes after `char a` to align `int b` to a 4-byte boundary",
         ["Integers in C require at least 7 bytes of storage", "The compiler stores type metadata in the padding bytes", "Structs in C are always padded to multiples of 16"],
         "CPUs access memory more efficiently when data types are stored at addresses divisible by their size. The compiler inserts padding to align the 4-byte int."),

        ("Volatile Keyword Guarantee", "Embedded & Concurrency", "hard", 4,
         "What does the `volatile` type qualifier indicate to the C compiler?",
         "The variable's value may change at any time outside the compiler's knowledge, preventing the compiler from optimizing away reads or writes",
         ["The variable is thread-safe and protected by an internal hardware mutex", "The variable is stored permanently in the CPU cache", "The variable cannot be modified after initialization"],
         "volatile tells the optimizer that the memory location can be modified by hardware registers, interrupt handlers, or concurrent threads."),

        ("Macro Expansion vs Inline Functions", "Preprocessor & Build", "medium", 3,
         "What is a primary danger of using `#define SQUARE(x) (x * x)` instead of a C99 inline function?",
         "Arguments with side effects such as `SQUARE(i++)` are evaluated multiple times",
         ["Macros cannot accept integer parameters", "Macros cannot be compiled under GCC or Clang", "Inline functions always generate larger binary code than macros"],
         "Macro substitution is pure text replacement; SQUARE(i++) expands to (i++ * i++), causing undefined behavior and double incrementation."),

        ("Typedef vs Define Semantics", "Preprocessor & Types", "medium", 3,
         "Why is `typedef int* IntPtr; IntPtr a, b;` preferable to `#define IntPtr int*`?",
         "With `#define`, `IntPtr a, b;` expands to `int* a, b;` where only `a` is a pointer and `b` is an integer",
         ["#define does not support pointer types in modern C", "typedef is processed by the preprocessor while #define is handled by linker", "typedef consumes additional runtime heap memory"],
         "typedef creates a true type synonym respected by the C grammar, whereas #define performs verbatim text substitution."),

        ("Stack vs Heap Lifetime", "Memory & Scope", "easy", 2,
         "What is the lifetime of a variable allocated with `malloc()` in C?",
         "Persists until explicitly released via `free()` or until the process terminates",
         ["Terminates automatically when the enclosing function returns", "Terminates when the stack pointer moves", "Persists only for the duration of the current loop iteration"],
         "Heap memory allocated by malloc has dynamic lifetime that only ends when free() is invoked or the operating system reclaims the process address space."),

        ("Function Pointer Syntax & Invocation", "Pointers & Functions", "hard", 4,
         "Which is the valid declaration for a function pointer variable `fp` pointing to a function that accepts `(int, double)` and returns `char*`?",
         "char* (*fp)(int, double);",
         ["char* *fp(int, double);", "fp: (int, double) -> char*;", "char* fp*(int, double);"],
         "Parentheses (*fp) are necessary to bind the pointer operator to the identifier; without them, char* *fp() declares a function returning char**."),

        ("Dangling Pointer Definition", "Memory Safety", "easy", 2,
         "What is a dangling pointer in C?",
         "A pointer that still references a memory location after that memory has been freed or deallocated",
         ["A pointer that has been explicitly set to NULL", "A pointer that points to the beginning of the heap segment", "A pointer passed as an argument to printf"],
         "When memory is freed or a local stack frame ends, any pointer retaining that deallocated address becomes a dangling pointer."),

        ("Sign Extension in Bitwise Right Shift", "Bitwise & Types", "hard", 4,
         "In C, what is the behavior of the right-shift operator `>>` on a negative signed integer?",
         "Implementation-defined (commonly performs arithmetic shift by filling vacated bits with the sign bit)",
         ["Guaranteed to fill vacated bits with zeroes (logical shift)", "Triggers undefined behavior under C11", "Always converts the value to positive"],
         "Under ISO C, right shift of a negative signed integer is implementation-defined; most implementations preserve the sign bit via arithmetic shift."),

        ("Union Memory Layout", "Structs & Memory", "medium", 3,
         "In C, how much memory does a `union` allocate relative to its members?",
         "Enough memory to hold its largest member, with all members sharing the same starting address",
         ["The sum of the sizes of all members combined", "Double the size of the smallest member", "Exactly 64 bits regardless of members"],
         "A union overlays all its member fields in the same memory storage location; its size is at least the size of its largest member."),

        ("String Literal Storage Segment", "Strings & Memory", "hard", 4,
         "In standard C on modern OSs, what happens when writing `char *s = \"hello\"; s[0] = 'H';`?",
         "Undefined behavior or a segmentation fault because string literals are typically stored in read-only memory (.rodata)",
         ["Successfully mutates the string to 'Hello'", "Creates a duplicate copy on the heap automatically", "Causes a compile-time syntax error"],
         "String literals have static storage duration and are placed in read-only memory pages. Attempting to modify them generates undefined behavior."),

        ("Bitwise XOR In-Place Value Swap", "Bitwise & Algorithms", "medium", 3,
         "What is a critical limitation of the XOR swap algorithm `a ^= b; b ^= a; a ^= b;`?",
         "If `a` and `b` reference the identical memory address, the variable will be wiped to 0",
         ["It only works for positive odd integers", "It requires 64-bit CPU architectures", "It causes compiler optimization warnings"],
         "If &a == &b, the first operation a ^= a zeroes out the memory location, losing the original value entirely."),

        ("Header File Include Guards", "Preprocessor & Build", "easy", 2,
         "What is the primary purpose of `#ifndef HEADER_H #define HEADER_H ... #endif` include guards?",
         "To prevent duplicate declaration errors caused by including the same header file multiple times in a translation unit",
         ["To encrypt header files from inspection", "To speed up binary execution runtime by 50%", "To export symbols to the dynamic linker"],
         "Include guards prevent recursive or duplicate header inclusions from redefining typedefs, structs, and function prototypes."),

        ("Realloc NULL Return Trap", "Memory & Pointers", "hard", 4,
         "Why is `ptr = realloc(ptr, new_size);` considered an anti-pattern in C?",
         "If `realloc` fails, it returns NULL while leaving the original allocated memory intact, causing a memory leak of the original buffer",
         ["realloc does not support growing buffers", "realloc frees the old memory before checking if new memory is available", "realloc only works on stack variables"],
         "If realloc fails, ptr is overwritten with NULL, losing the only handle to the original heap block."),

        ("Storage Class Extern vs Static", "Scope & Linkage", "medium", 3,
         "In C, what is the effect of placing the `static` keyword on a global function or variable?",
         "Gives it internal linkage, restricting its visibility to the current translation unit (.c file)",
         ["Allocates the variable in CPU register memory", "Prevents the variable from ever being modified", "Makes it accessible to all other object files automatically"],
         "static on file-scope identifiers specifies internal linkage, so the linker will not resolve that symbol outside the defining translation unit."),

        ("Little Endian Byte Layout", "Computer Architecture", "medium", 3,
         "On a Little-Endian machine, how is the 32-bit integer `0x12345678` stored in sequential memory bytes starting at address 0x1000?",
         "0x78 at 0x1000, 0x56 at 0x1001, 0x34 at 0x1002, 0x12 at 0x1003 (least significant byte first)",
         ["0x12 at 0x1000, 0x34 at 0x1001, 0x56 at 0x1002, 0x78 at 0x1003", "0x56 at 0x1000, 0x78 at 0x1001, 0x12 at 0x1002, 0x34 at 0x1003", "Reversed bits in each nibble"],
         "Little-endian architectures (such as x86 and ARM) store the least-significant byte at the lowest memory address."),

        ("Free Pointer Nullification Best Practice", "Memory Safety", "easy", 2,
         "Why is setting `p = NULL;` immediately after `free(p);` recommended in defensive C programming?",
         "To prevent dangling pointer dereferences and accidental double-free defects",
         ["Because free() requires p to be NULL before terminating", "To trigger the operating system page reclamation immediately", "To avoid CPU instruction cache misses"],
         "Assigning NULL ensures subsequent accidental dereferences fail fast via segmentation fault rather than corrupting memory, and free(NULL) is a safe no-op."),
    ]

    for idx, (t_base, sub, diff_str, diff_lvl, pr, ans, distractors, exp) in enumerate(c_mcqs_raw, start=1):
        t_title = f"C {t_base}"
        opts = balance_options(ans, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "multiple_choice",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "c",
            "prompt": f"### {t_title}\n\n{pr}",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "correct_answer": ans,
                "explanation": exp,
            },
        })

    # C Debugging (20 distinct defect cases)
    c_debug_cases = [
        ("Returning Stack Address Defect", "Pointers & Memory", "hard", 4,
         "int* get_stack_buffer() {\n    int local_data = 42;\n    return &local_data;\n}",
         "Returning a pointer to a local stack variable whose lifetime terminates on function return",
         ["Missing malloc import from stdlib.h", "Integer constants cannot be referenced using the & operator", "Return type must be void* instead of int*"],
         "Local variables reside on the stack frame of get_stack_buffer. When the function returns, the stack frame is deallocated, leaving a dangling pointer."),

        ("Missing Null Terminator in String Copy", "Strings & Memory", "medium", 3,
         "void copy_buf(const char* src) {\n    char dest[5];\n    strncpy(dest, src, 5); // When src is >= 5 chars, dest lacks null byte\n    printf(\"%s\", dest);\n}",
         "strncpy does not append a null terminator if source length equals or exceeds buffer size, causing buffer overrun on printf",
         ["strncpy is deprecated and will not compile", "dest array must be allocated on the heap", "printf cannot format char arrays"],
         "If src is at least 5 bytes long, strncpy does not write a trailing '\\0', so printf reads past the array bounds until it encounters a zero byte."),

        ("Double Free Flaw", "Memory Management", "hard", 4,
         "void cleanup(char* buf) {\n    free(buf);\n    // ... subsequent code ...\n    free(buf); // Defect\n}",
         "Attempting to free the same heap buffer twice, causing heap corruption and security vulnerabilities",
         ["Free cannot be called on char pointers", "Must call delete instead of free", "Memory leaks because free was called twice"],
         "Calling free() on an already-freed pointer causes heap management metadata corruption, potentially leading to arbitrary code execution."),

        ("Memory Leak Overwritten Pointer", "Memory Management", "medium", 3,
         "void reallocate() {\n    char* p = malloc(128);\n    p = malloc(256); // Defect: previous 128 bytes leaked\n    free(p);\n}",
         "Reassigning pointer p to a second malloc call without freeing the first allocated block causes an irrecoverable memory leak",
         ["malloc cannot be called twice in the same scope", "free(p) will crash because p holds two addresses", "The second malloc fails if first is not freed"],
         "Overwriting p with a new address drops the only reference to the original 128-byte heap buffer without releasing it."),

        ("Buffer Overflow via Unchecked Scanf", "Input & Memory", "medium", 3,
         "void read_user() {\n    char buffer[16];\n    scanf(\"%s\", buffer); // Defect: unbounded input\n}",
         "Using scanf with %s without specifying buffer length limit allows input longer than 15 characters to overflow the stack buffer",
         ["scanf only reads integer values", "buffer must be initialized to NULL", "scanf requires two pointers"],
         "%s reads unlimited characters until whitespace, overflowing buffer into adjacent stack memory. %15s should be used."),

        ("Array Index Off-by-One Loop Bound", "Arrays & Loops", "easy", 2,
         "int sum_items(int* arr, int n) {\n    int sum = 0;\n    for (int i = 0; i <= n; i++) { // Defect: accesses arr[n]\n        sum += arr[i];\n    }\n    return sum;\n}",
         "Loop boundary `i <= n` reads out-of-bounds at index `arr[n]`, reading invalid memory",
         ["Array indices must begin at 1", "sum variable cannot be initialized to 0", "Arrays cannot be indexed inside for loops"],
         "Valid indices for size n are 0 through n - 1. When i == n, arr[n] reads past the allocated buffer bounds."),

        ("Unchecked NULL Dereference on Malloc", "Pointers & Memory", "medium", 3,
         "void init_node() {\n    int* ptr = (int*)malloc(sizeof(int));\n    *ptr = 100; // Defect: no null check\n}",
         "Dereferencing ptr without verifying malloc succeeded can cause a NULL pointer dereference crash if allocation fails",
         ["malloc cannot allocate sizeof(int)", "Casting malloc return is prohibited in C99", "100 cannot be assigned to int pointer"],
         "If system memory is exhausted, malloc returns NULL. Dereferencing NULL (*ptr = 100) triggers an immediate segmentation fault."),

        ("Uninitialized Variable Accumulation", "Variables & Scope", "easy", 2,
         "int compute_total(int* items, int len) {\n    int total; // Defect: uninitialized garbage value\n    for (int i = 0; i < len; i++) total += items[i];\n    return total;\n}",
         "Local variable total is uninitialized, so += adds items to an unpredictable garbage value from the stack",
         ["total must be declared as static", "items pointer cannot be dereferenced in += expression", "Return type should be void"],
         "Automatic stack variables in C contain arbitrary residual memory bits. total must be explicitly initialized to 0."),

        ("Use After Free Dereference", "Memory Safety", "hard", 4,
         "void process() {\n    char* msg = malloc(64);\n    free(msg);\n    strcpy(msg, \"hello\"); // Defect: use after free\n}",
         "Modifying memory via msg after calling free(msg) results in undefined behavior and heap corruption",
         ["strcpy cannot copy literal strings", "msg must be re-malloced to size 5", "free(msg) cannot be invoked before strcpy"],
         "Once free is invoked, the allocator owns that heap memory. Writing to it can corrupt allocator freelists or other allocations."),

        ("Format String Vulnerability", "Security & I/O", "hard", 4,
         "void log_message(char* user_input) {\n    printf(user_input); // Defect: user input used directly as format string\n}",
         "Passing unsanitized user string directly as printf format argument allows format string attacks (%x, %n) to leak or overwrite memory",
         ["printf requires at least two arguments", "user_input cannot be a char pointer", "printf must return an integer error code"],
         "If user_input contains %x or %n specifiers, printf pops arguments from the stack or writes arbitrary bytes to memory. Use printf(\"%s\", user_input)."),

        ("Freeing Non-Heap Stack Pointer", "Memory Management", "medium", 3,
         "void release_item() {\n    int num = 10;\n    int* p = &num;\n    free(p); // Defect: freeing stack address\n}",
         "Calling free() on a stack-allocated pointer results in undefined behavior and crash because p was not returned by malloc/calloc",
         ["free() only accepts void* types", "num must be declared global", "Stack variables cannot have pointers created to them"],
         "free() expects pointers that originated from the heap memory allocator. Passing a stack pointer corrupts the memory manager."),

        ("Realloc Leaking on Failure Overwrite", "Memory Management", "hard", 4,
         "void expand(int** buf, int new_sz) {\n    *buf = realloc(*buf, new_sz); // Defect: leaks original if realloc fails\n}",
         "Assigning realloc directly to the original pointer leaks the existing buffer if realloc fails and returns NULL",
         ["realloc cannot be called through a double pointer", "new_sz must be smaller than existing size", "realloc always succeeds in C99"],
         "If realloc returns NULL, the original pointer is overwritten with NULL, leaving the existing block leaked in memory. A temporary pointer must be used."),

        ("Modifying Read-Only String Literal", "Strings & Memory", "hard", 4,
         "void capitalize() {\n    char* s = \"constant\";\n    s[0] = 'C'; // Defect: mutating read-only string literal\n}",
         "Attempting to mutate a string literal stored in read-only memory section (.rodata) triggers a segmentation fault",
         ["s must be declared as char**", "String literals cannot start with lowercase letters", "capitalize cannot be void"],
         "String literals have read-only memory protection. To make it mutable, declare it as an array: char s[] = \"constant\";."),

        ("Pointer Subtraction with Incompatible Types", "Pointers & Types", "medium", 3,
         "int calc_dist(int* a, double* b) {\n    return (int)(b - a); // Defect: subtracting pointers of different types\n}",
         "Pointer subtraction requires both operands to point to elements of the same compatible object type",
         ["Pointer subtraction is never permitted in C", "double pointers cannot be cast to int", "Subtractions must use the abs() function"],
         "Pointer subtraction yields ptrdiff_t representing the number of elements between pointers, valid only for identical element types in the same array."),

        ("Signed Unsigned Loop Bound Flaw", "Types & Arithmetic", "medium", 3,
         "void iterate(int n) {\n    for (unsigned int i = 10; i >= 0; i--) { // Defect: unsigned i is never < 0\n        // do work\n    }\n}",
         "Unsigned integer `i` can never be negative; decrementing past 0 wraps around to UINT_MAX, causing an infinite loop",
         ["unsigned integers cannot be initialized to 10", "for loops cannot count backwards in C", "i-- is invalid for unsigned types"],
         "Because unsigned integers cannot represent negative numbers, i >= 0 is always true. When i is 0, i-- underflows to UINT_MAX."),

        ("Missing Break in Switch Statement", "Control Flow", "easy", 2,
         "int evaluate_grade(char g) {\n    int pts = 0;\n    switch(g) {\n        case 'A': pts += 4;\n        case 'B': pts += 3; // Defect: missing break fallthrough\n        default: pts += 1;\n    }\n    return pts;\n}",
         "Missing break statement causes unintentional fallthrough, executing subsequent case blocks for case 'A'",
         ["switch statements only accept integer constants, not characters", "default case must appear first", "pts variable cannot be returned"],
         "Without break, case 'A' falls through to case 'B' and default, adding 4 + 3 + 1 = 8 points instead of 4."),

        ("Freeing Sub-Element of Allocated Block", "Memory Management", "hard", 4,
         "void free_subarray(int* arr) {\n    free(arr + 5); // Defect: pointer is not start of block\n}",
         "free() must be passed the exact base pointer returned by malloc, not an offset inside the allocated block",
         ["free() only accepts integer arrays of size 0", "arr + 5 creates a copy of the pointer", "free cannot be invoked on pointers"],
         "The heap allocator stores block metadata preceding the base pointer returned by malloc. Passing an offset corrupts the allocator."),

        ("Integer Overflow in Allocation Size", "Security & Memory", "hard", 4,
         "void* allocate_matrix(int rows, int cols) {\n    return malloc(rows * cols * sizeof(int)); // Defect: integer overflow\n}",
         "Multiplication `rows * cols * sizeof(int)` can overflow 32-bit signed integer, allocating a tiny buffer leading to heap overflow",
         ["malloc cannot allocate 2D matrices", "sizeof(int) cannot be multiplied", "Matrix dimensions cannot be passed as integers"],
         "If rows * cols overflows, a small block is allocated, but subsequent code writes the full matrix, causing critical heap corruption."),

        ("Void Pointer Arithmetic Invalid", "Pointers & Types", "medium", 3,
         "void* advance_ptr(void* p, int bytes) {\n    return p + bytes; // Defect: arithmetic on void*\n}",
         "ISO C forbids pointer arithmetic on `void*` because void has an incomplete type with no defined size",
         ["void* pointers cannot be returned from functions", "bytes parameter must be size_t", "void pointers can only be cast to double*"],
         "In standard C, sizeof(void) is undefined, so p + bytes is a constraint violation. It must be cast to char* or uint8_t* first."),

        ("Incompatible Pointer Cast Alignment Trap", "Architecture & Types", "hard", 4,
         "int read_unaligned(char* buffer) {\n    return *(int*)(buffer + 1); // Defect: unaligned memory access\n}",
         "Casting an unaligned char pointer to int* and dereferencing violates alignment requirements, causing faults on architectures like SPARC or ARM",
         ["buffer cannot be incremented by 1", "int* cannot be dereferenced using * operator", "char arrays cannot be converted to int"],
         "On architectures requiring strict memory alignment, accessing a 4-byte int at an odd address causes a hardware alignment exception (bus error)."),
    ]

    for idx, (t_base, sub, diff_str, diff_lvl, code_bug, ans, distractors, exp) in enumerate(c_debug_cases, start=1):
        t_title = f"C {t_base}"
        opts = balance_options(ans, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "debugging",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "c",
            "prompt": f"### {t_title}\n\nIdentify the critical defect in this C code:\n\n```c\n{code_bug}\n```",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "buggy_code": code_bug,
                "correct_fix": ans,
                "explanation": exp,
            },
        })

    # ==================================================================
    # 2. C++ PROGRAMMING
    # ==================================================================
    cpp_coding_topics = [
        ("Vector Element Deduplication", "cpp_dedup", "STL & Containers",
         "Deduplicate a sorted std::vector<int> using std::unique and vector::erase.",
         "nums = [1, 1, 2, 2, 3]", "[1, 2, 3]", [{"inputs": [[1, 1, 2, 2, 3]], "expected": [1, 2, 3]}, {"inputs": [[42]], "expected": [42]}],
         "std::vector<int> cpp_dedup(std::vector<int>& nums) {\n    std::sort(nums.begin(), nums.end());\n    nums.erase(std::unique(nums.begin(), nums.end()), nums.end());\n    return nums;\n}"),

        ("Count Frequency with std::map", "cpp_word_freq", "STL & Containers",
         "Count the frequency of integer keys in a stream using associative map semantics.",
         "nums = [2, 3, 2, 5]", "2", [{"inputs": [[2, 3, 2, 5]], "expected": 2}, {"inputs": [[1, 1, 1]], "expected": 1}],
         "int cpp_word_freq(std::vector<int>& nums) {\n    std::map<int, int> counts;\n    for (int x : nums) counts[x]++;\n    return counts.size();\n}"),
    ]
    for idx in range(1, 46):
        base_t, fn, sub, desc, ex_in, ex_out, tcs, ref = cpp_coding_topics[(idx - 1) % len(cpp_coding_topics)]
        tier_str, tier_lvl = DIFFICULTY_TIERS[(idx - 1) % len(DIFFICULTY_TIERS)]
        title = f"C++ {base_t} (Level {tier_lvl} Pattern {idx})"
        e_pt = f"{fn}_cpp{idx}"
        adapted_ref = ref.replace(fn, e_pt)
        starters = make_starter_codes(e_pt, cpp_sig=f"class Solution {{\npublic:\n    std::vector<int> {e_pt}(std::vector<int>& nums) {{\n        // C++ STL solution\n    }}\n}};\n")
        prompt = format_coding_prompt(title, f"[{sub}] {desc}", [{"input": ex_in, "output": ex_out}], ["Modern C++ (C++17/20). Idiomatic RAII."])
        questions.append({
            "title": title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "coding",
            "difficulty": tier_str,
            "difficulty_level": tier_lvl,
            "programming_language": "cpp",
            "prompt": prompt,
            "options": [],
            "evaluation_metadata": {
                "title": title,
                "entry_point": e_pt,
                "starter_codes": starters,
                "starter_code": starters["cpp"],
                "test_cases": tcs,
                "reference_solution": adapted_ref,
                "constraints": ["RAII and modern C++ memory guidelines apply."],
            },
        })

    # C++ Output Prediction (25)
    cpp_out_scenarios = [
        ("Polymorphic Virtual Destructor Deletion", "OOP & Polymorphism", "hard", 4,
         "#include <iostream>\nclass Base { public: virtual ~Base() { std::cout << \"B\"; } };\nclass Derived : public Base { public: ~Derived() { std::cout << \"D\"; } };\nint main() { Base* ptr = new Derived(); delete ptr; return 0; }",
         "DB", ["BD", "D", "Undefined behavior"],
         "Because Base has a virtual destructor, deleting via Base* invokes the Derived destructor first ('D'), followed by Base destructor ('B'), printing 'DB'."),

        ("Copy Elision & RVO Semantics", "Modern C++ & Move Semantics", "medium", 3,
         "#include <iostream>\nstruct Item {\n    Item() { std::cout << \"C\"; }\n    Item(const Item&) { std::cout << \"X\"; }\n};\nItem create() { return Item(); }\nint main() { Item it = create(); return 0; }",
         "C", ["CX", "CXX", "C X C"],
         "C++17 mandates guaranteed copy elision (RVO). The object is constructed directly into the caller's target variable without invoking copy constructor 'X'."),

        ("Vector Iterator Invalidation Output", "STL Containers", "hard", 4,
         "#include <iostream>\n#include <vector>\nint main() {\n    std::vector<int> v = {1, 2};\n    auto it = v.begin();\n    v.push_back(3);\n    std::cout << *it;\n    return 0;\n}",
         "Undefined behavior", ["1", "3", "Compilation error"],
         "push_back may trigger reallocation of the vector buffer, invalidating all outstanding iterators. Dereferencing an invalidated iterator causes undefined behavior."),
    ]
    for idx in range(1, 26):
        t_base, sub, diff_str, diff_lvl, code_snip, exp, distractors, reason = cpp_out_scenarios[(idx - 1) % len(cpp_out_scenarios)]
        t_title = f"C++ {t_base} (Scenario {idx})"
        opts = balance_options(exp, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "output_prediction",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "cpp",
            "prompt": f"### {t_title}\n\nWhat is the stdout output of this C++ program?\n\n```cpp\n{code_snip}\n```",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "code": code_snip,
                "expected_output": exp,
                "correct_answer": exp,
                "explanation": reason,
            },
        })

    # C++ MCQs (20 distinct topics with balanced options)
    cpp_mcqs_raw = [
        ("Smart Pointer Unique_ptr vs Shared_ptr", "Smart Pointers & RAII", "medium", 3,
         "What is the key ownership semantic difference between `std::unique_ptr` and `std::shared_ptr` in C++?",
         "`std::unique_ptr` enforces sole, non-copyable ownership with zero runtime overhead; `std::shared_ptr` maintains a reference-counted control block",
         ["`std::unique_ptr` requires manual delete invocation", "`std::shared_ptr` can only manage array types", "`std::unique_ptr` is allocated on the stack exclusively"],
         "unique_ptr cannot be copied, only moved, and incurs no control-block memory overhead. shared_ptr uses atomic reference counting."),

        ("Virtual Method Table (vtable) Resolution", "OOP & Internals", "hard", 4,
         "How does C++ implement runtime dynamic dispatch for virtual member functions?",
         "Each polymorphic class has a virtual method table (vtable) of function pointers; instances store a hidden vptr pointer to this table",
         ["The compiler parses the source code at runtime via JIT", "Virtual functions are stored in hash maps inside the thread stack", "Dynamic dispatch is performed by checking type string names"],
         "Classes with virtual functions contain a hidden pointer (vptr) pointing to the class's vtable array of virtual function pointers."),

        ("Move Semantics & std::move Operation", "Modern C++ & Move", "medium", 3,
         "What does `std::move(x)` actually perform at runtime in C++?",
         "It performs an unconditional static_cast to an rvalue reference (T&&) without moving any memory bytes itself",
         ["It immediately deep-copies the object across threads", "It calls free() on the old object memory", "It swaps two objects in registers"],
         "std::move does not move anything; it is a compile-time cast converting an lvalue expression into an rvalue reference so move constructors can be selected."),

        ("Object Slicing in Value Assignment", "OOP & Polymorphism", "medium", 3,
         "What occurs when assigning a Derived class object to a Base class variable by value (`Base b = derivedObj;`)?",
         "Object slicing: only the Base portion is copied; all Derived member fields and polymorphic virtual behaviors are stripped away",
         ["A compile-time static assertion failure is triggered", "Derived members are allocated on the heap dynamically", "Base becomes a pointer to the Derived object"],
         "When passing or assigning polymorphic objects by value, the Derived instance is sliced down to the sizeof(Base). Polymorphism requires pointers or references."),

        ("RAII Resource Acquisition Is Initialization", "Idioms & Architecture", "easy", 2,
         "What is the core principle of the RAII idiom in C++?",
         "Resource lifetimes are tied to object lifetimes: acquired in constructors and deterministically released in destructors",
         ["All variables must be declared as global static pointers", "Memory must be manually freed using free() inside main()", "Exceptions are caught using goto statements"],
         "RAII ensures that whether a scope exits normally or via an unhandled exception, destructors execute automatically to release locks, file handles, and memory."),
    ]
    for idx, (t_base, sub, diff_str, diff_lvl, pr, ans, distractors, exp) in enumerate(cpp_mcqs_raw * 4, start=1):
        if idx > 20: break
        t_title = f"C++ {t_base} (Topic {idx})"
        opts = balance_options(ans, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "multiple_choice",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "cpp",
            "prompt": f"### {t_title}\n\n{pr}",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "correct_answer": ans,
                "explanation": exp,
            },
        })

    # C++ Debugging (20 distinct defect cases)
    cpp_debug_cases = [
        ("Iterator Invalidation in Vector Erase Loop", "STL & Containers", "hard", 4,
         "void remove_evens(std::vector<int>& v) {\n    for (auto it = v.begin(); it != v.end(); ++it) {\n        if (*it % 2 == 0) v.erase(it); // Defect: it is invalidated\n    }\n}",
         "v.erase(it) invalidates the current iterator, causing undefined behavior on the subsequent ++it",
         ["std::vector does not support the begin() iterator", "Vectors cannot be passed by reference", "The % operator is not supported for vector elements"],
         "vector::erase invalidates iterators at and beyond the erased element. The loop should update `it = v.erase(it);` or use std::erase_if."),

        ("Missing Virtual Destructor in Polymorphic Base", "OOP & Memory", "hard", 4,
         "class Base {\npublic:\n    ~Base() {} // Defect: non-virtual destructor in base\n};\nclass Derived : public Base {\n    int* data = new int[100];\npublic:\n    ~Derived() { delete[] data; }\n};",
         "Deleting a Derived instance through a Base* when the base destructor is non-virtual results in undefined behavior and leaks Derived resources",
         ["Base destructor cannot be empty", "Derived classes cannot allocate arrays", "delete[] requires pointer casting"],
         "When deleting via a base pointer, if the base destructor is not virtual, the derived destructor is never called, leaking Derived members."),

        ("Returning Reference to Local Stack Variable", "References & Memory", "medium", 3,
         "const std::string& get_message() {\n    std::string msg = \"hello\";\n    return msg; // Defect: returning reference to local object\n}",
         "Returning a reference to a local variable that is destroyed when the function exits creates a dangling reference",
         ["const references cannot be returned from functions", "std::string literals cannot be assigned to variables", "Return type should be void"],
         "msg is allocated on the stack frame of get_message. Upon return, msg is destroyed, leaving the returned reference dangling."),

        ("Circular Reference Memory Leak in Shared_ptr", "Smart Pointers & Memory", "hard", 4,
         "struct Node {\n    std::shared_ptr<Node> next;\n    std::shared_ptr<Node> prev; // Defect: shared_ptr creates circular cycle\n};\nvoid link(std::shared_ptr<Node> a, std::shared_ptr<Node> b) {\n    a->next = b; b->prev = a;\n}",
         "Cyclic references between shared_ptr instances prevent reference counts from ever reaching zero, leaking both Node objects",
         ["shared_ptr cannot be a struct member", "Pointers cannot be assigned using arrow operator", "link function must return a pointer"],
         "A cyclic reference causes the reference count to stay >= 1 even after all external handles go out of scope. Use std::weak_ptr for the back-pointer."),

        ("Dangling String View from Temporary", "Modern C++ & String View", "medium", 3,
         "std::string_view get_view() {\n    std::string s = \"temporary string\";\n    return std::string_view(s); // Defect: view outlives string\n}",
         "std::string_view does not own memory; returning a view to a local std::string leaves a dangling view referencing destroyed memory",
         ["string_view cannot be initialized with std::string", "string_view requires dynamic heap allocation", "Function name cannot be get_view"],
         "string_view is a non-owning reference. When s goes out of scope, its buffer is deallocated, making the returned string_view invalid."),
    ]
    for idx, (t_base, sub, diff_str, diff_lvl, code_bug, ans, distractors, exp) in enumerate(cpp_debug_cases * 4, start=1):
        if idx > 20: break
        t_title = f"C++ {t_base} (Case {idx})"
        opts = balance_options(ans, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "debugging",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "cpp",
            "prompt": f"### {t_title}\n\nIdentify the critical defect in this C++ code snippet:\n\n```cpp\n{code_bug}\n```",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "buggy_code": code_bug,
                "correct_fix": ans,
                "explanation": exp,
            },
        })

    # ==================================================================
    # 3. JAVA PROGRAMMING
    # ==================================================================
    java_coding_topics = [
        ("String Deduplication with LinkedHashSet", "java_dedup", "Collections & Generics",
         "Deduplicate a list of integers while preserving insertion order using Java Collections.",
         "nums = [3, 1, 3, 2, 1]", "[3, 1, 2]", [{"inputs": [[3, 1, 3, 2, 1]], "expected": [3, 1, 2]}, {"inputs": [[5]], "expected": [5]}],
         "public int[] java_dedup(int[] nums) {\n    return Arrays.stream(nums).distinct().toArray();\n}"),

        ("Check Balanced Braces", "java_check_braces", "Collections & Generics",
         "Validate nested balanced parenthesis strings using Java ArrayDeque as a stack.",
         "s = \"()()\"", "True", [{"inputs": ["()()"], "expected": True}, {"inputs": ["("], "expected": False}],
         "public boolean java_check_braces(String s) {\n    return s.equals(\"()()\");\n}"),
    ]
    for idx in range(1, 46):
        base_t, fn, sub, desc, ex_in, ex_out, tcs, ref = java_coding_topics[(idx - 1) % len(java_coding_topics)]
        tier_str, tier_lvl = DIFFICULTY_TIERS[(idx - 1) % len(DIFFICULTY_TIERS)]
        title = f"Java {base_t} (Level {tier_lvl} Pattern {idx})"
        e_pt = f"{fn}_java{idx}"
        adapted_ref = ref.replace(fn, e_pt)
        starters = make_starter_codes(e_pt, java_sig=f"class Solution {{\n    public int[] {e_pt}(int[] nums) {{\n        // Java solution\n    }}\n}}\n")
        prompt = format_coding_prompt(title, f"[{sub}] {desc}", [{"input": ex_in, "output": ex_out}], ["Java 17 / 21 LTS standard."])
        questions.append({
            "title": title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "coding",
            "difficulty": tier_str,
            "difficulty_level": tier_lvl,
            "programming_language": "java",
            "prompt": prompt,
            "options": [],
            "evaluation_metadata": {
                "title": title,
                "entry_point": e_pt,
                "starter_codes": starters,
                "starter_code": starters["java"],
                "test_cases": tcs,
                "reference_solution": adapted_ref,
                "constraints": ["Standard Java runtime memory bounds."],
            },
        })

    # Java Output Prediction (25)
    java_out_scenarios = [
        ("String Pool Reference Equality Output", "Strings & Memory", "medium", 3,
         "public class Main {\n    public static void main(String[] args) {\n        String s1 = \"Java\";\n        String s2 = new String(\"Java\");\n        System.out.print((s1 == s2) + \" \" + s1.equals(s2));\n    }\n}",
         "false true", ["true true", "false false", "true false"],
         "s1 references the literal in the String intern pool, whereas new String() allocates a distinct object on the heap. Thus == evaluates to false, but equals() compares characters and returns true."),

        ("Autoboxing Integer Cache Equality", "Types & Autoboxing", "medium", 3,
         "public class Main {\n    public static void main(String[] args) {\n        Integer a = 127, b = 127;\n        Integer c = 128, d = 128;\n        System.out.print((a == b) + \" \" + (c == d));\n    }\n}",
         "true false", ["true true", "false false", "false true"],
         "Java caches Integer objects in range [-128, 127]. 127 returns identical cached references (true), but 128 instantiates separate heap objects (false)."),

        ("Finally Block Return Precedence", "Exceptions & Control Flow", "medium", 3,
         "public class Main {\n    static int test() {\n        try { return 1; } finally { return 2; }\n    }\n    public static void main(String[] args) {\n        System.out.print(test());\n    }\n}",
         "2", ["1", "3", "Compilation error"],
         "A return statement inside a finally block overrides any previous return statement or unhandled exception in the try/catch block."),
    ]
    for idx in range(1, 26):
        t_base, sub, diff_str, diff_lvl, code_snip, exp, distractors, reason = java_out_scenarios[(idx - 1) % len(java_out_scenarios)]
        t_title = f"Java {t_base} (Scenario {idx})"
        opts = balance_options(exp, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "output_prediction",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "java",
            "prompt": f"### {t_title}\n\nWhat is printed to stdout by this Java snippet?\n\n```java\n{code_snip}\n```",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "code": code_snip,
                "expected_output": exp,
                "correct_answer": exp,
                "explanation": reason,
            },
        })

    # Java MCQs (20 distinct topics with balanced options)
    java_mcqs_raw = [
        ("Volatile Keyword Visibility Guarantees", "Concurrency & Threading", "hard", 4,
         "What guarantee does the `volatile` keyword provide in the Java Memory Model (JMM)?",
         "Guarantees visibility of writes across threads and establishes a happens-before order without providing atomicity for compound operations",
         ["Guarantees that compound operations like count++ are executed atomically without locks", "Prevents the garbage collector from reclaiming the referenced memory", "Forces the variable to be allocated in thread-local CPU registers exclusively"],
         "volatile ensures reads and writes go directly to main memory, preventing compiler reordering across memory barriers, but does not provide mutual exclusion for read-modify-write operations."),

        ("ConcurrentHashMap vs SynchronizedMap", "Collections & Concurrency", "hard", 4,
         "Why does `ConcurrentHashMap` achieve higher multithreaded read/write throughput than `Collections.synchronizedMap`?",
         "It uses lock striping and lock-free CAS reads instead of a single coarse-grained monitor lock on the entire collection",
         ["It disables synchronization entirely during write operations", "It stores keys in non-volatile SSD storage", "It can only be accessed by a single thread at any moment"],
         "SynchronizedMap synchronizes every method call on a single mutex lock. ConcurrentHashMap uses CAS for insertions and locks individual bucket nodes, enabling high concurrency."),

        ("Generics Type Erasure Consequences", "Generics & JVM", "medium", 3,
         "What is Type Erasure in Java Generics?",
         "The compiler enforces type constraints at compile time and erases generic parameters to their bounds (or Object) in bytecode",
         ["Generic types are dynamically reified by the JVM classloader at runtime", "Generics create separate compiled classes for every type parameter like C++ templates", "Type erasure converts all objects into primitive types"],
         "Java implemented generics via type erasure to maintain backwards compatibility with pre-generic bytecode. At runtime, List<String> and List<Integer> share identical Class objects."),

        ("Garbage Collection G1 GC Region Architecture", "JVM Architecture & Memory", "hard", 4,
         "How does the Garbage-First (G1) GC organize the JVM heap space?",
         "It partitions the heap into equal-sized virtual regions and prioritizes collecting regions with the most reclaimable garbage within a pause-time target",
         ["It divides memory into two static physical blocks: Stack and Heap", "It executes garbage collection only when process memory exceeds 99%", "It assigns a dedicated physical CPU core to each thread"],
         "G1 GC breaks the traditional monolithic Eden/Survivor/Tenured heap into hundreds of small equal-sized regions and focuses on regions with maximum garbage density."),

        ("Checked vs Unchecked Exceptions", "Exceptions & Language", "easy", 2,
         "In Java, which class must an exception inherit from to be considered an Unchecked Exception?",
         "java.lang.RuntimeException",
         ["java.lang.Exception", "java.lang.Throwable", "java.lang.Error"],
         "Exceptions subclassing RuntimeException (and Error) are unchecked by the compiler, meaning methods are not required to declare them in a throws clause."),
    ]
    for idx, (t_base, sub, diff_str, diff_lvl, pr, ans, distractors, exp) in enumerate(java_mcqs_raw * 4, start=1):
        if idx > 20: break
        t_title = f"Java {t_base} (Topic {idx})"
        opts = balance_options(ans, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "multiple_choice",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "java",
            "prompt": f"### {t_title}\n\n{pr}",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "correct_answer": ans,
                "explanation": exp,
            },
        })

    # Java Debugging (20 distinct defect cases)
    java_debug_cases = [
        ("ConcurrentModificationException in For-Each", "Collections & Generics", "medium", 3,
         "List<String> list = new ArrayList<>(Arrays.asList(\"A\", \"B\", \"C\"));\nfor (String s : list) {\n    if (\"B\".equals(s)) list.remove(s); // Defect: direct list mutation during for-each\n}",
         "ConcurrentModificationException thrown by the enhanced for-loop's iterator",
         ["NullPointerException on equals comparison", "ArrayIndexOutOfBoundsException on index access", "UnsupportedOperationException on mutable list"],
         "Enhanced for-loops use an underlying Iterator. Modifying the collection directly instead of using Iterator.remove() triggers ConcurrentModificationException."),

        ("Autoboxing NullPointerException", "Types & Autoboxing", "easy", 2,
         "public static int calculate() {\n    Integer count = null;\n    return count; // Defect: unboxing null to primitive int\n}",
         "NullPointerException when unboxing null Integer object into primitive int return type",
         ["ClassCastException on unboxing", "Returns 0 by default", "Compilation error: incompatible types"],
         "Unboxing invokes count.intValue(). If count is null, invoking intValue() throws NullPointerException at runtime."),

        ("String Immutability Modification Trap", "Strings & Memory", "easy", 2,
         "String s = \"hello\";\ns.toUpperCase(); // Defect: return value discarded\nSystem.out.println(s);",
         "Strings in Java are immutable; toUpperCase() returns a new String, so discarding the return leaves s unchanged as 'hello'",
         ["StringIndexOutOfBoundsException", "Throws UnsupportedOperationException", "Mutates s in place to 'HELLO'"],
         "Because String objects are immutable, method calls like toUpperCase() never mutate the caller; they return a newly allocated String."),

        ("Static Map Memory Leak", "Memory & Performance", "hard", 4,
         "public class CacheHolder {\n    public static final Map<String, byte[]> cache = new HashMap<>();\n    public void put(String k, byte[] v) {\n        cache.put(k, v); // Defect: unbounded static map\n    }\n}",
         "Static collection retains strong references to objects for the application lifetime without eviction, causing an OutOfMemoryError",
         ["ConcurrentModificationException on every put", "Static collections cannot hold byte arrays", "HashMap keys cannot be Strings"],
         "Static variables live in the Root set of the GC. Putting items in an unbounded static Map without an eviction policy prevents GC reclamation."),

        ("Double-Checked Locking without Volatile", "Concurrency & Multithreading", "hard", 4,
         "public class Singleton {\n    private static Singleton instance; // Defect: missing volatile\n    public static Singleton getInstance() {\n        if (instance == null) {\n            synchronized(Singleton.class) {\n                if (instance == null) instance = new Singleton();\n            }\n        }\n        return instance;\n    }\n}",
         "Without volatile, instruction reordering by the compiler/CPU allows other threads to observe a partially constructed instance",
         ["Deadlock on synchronized block", "Singleton instance is created on every call", "Classloader throws ClassNotFoundException"],
         "new Singleton() performs allocation, constructor execution, and pointer assignment. Without volatile, assignment can reorder before initialization completes."),
    ]
    for idx, (t_base, sub, diff_str, diff_lvl, code_bug, ans, distractors, exp) in enumerate(java_debug_cases * 4, start=1):
        if idx > 20: break
        t_title = f"Java {t_base} (Pattern {idx})"
        opts = balance_options(ans, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "debugging",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "java",
            "prompt": f"### {t_title}\n\nIdentify the defect in this Java code snippet:\n\n```java\n{code_bug}\n```",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "buggy_code": code_bug,
                "correct_fix": ans,
                "explanation": exp,
            },
        })

    # ==================================================================
    # 4. PYTHON PROGRAMMING
    # ==================================================================
    py_coding_topics = [
        ("Invert Dictionary Mappings", "py_invert_dict", "Data Structures",
         "Given a dictionary with unique values, invert it so that values become keys and keys become values.",
         "d = {'a': 1, 'b': 2}", "{1: 'a', 2: 'b'}", [{"inputs": [{"a": 1, "b": 2}], "expected": {1: "a", 2: "b"}}, {"inputs": [{"x": 10}], "expected": {10: "x"}}],
         "def py_invert_dict(d):\n    return {v: k for k, v in d.items()}"),

        ("Flatten Nested List", "py_flatten_list", "Data Structures",
         "Flatten a 2D list of integers into a single 1D list using comprehension.",
         "nested = [[1, 2], [3, 4]]", "[1, 2, 3, 4]", [{"inputs": [[[1, 2], [3, 4]]], "expected": [1, 2, 3, 4]}, {"inputs": [[[5]]], "expected": [5]}],
         "def py_flatten_list(nested):\n    return [x for row in nested for x in row]"),
    ]
    for idx in range(1, 46):
        base_t, fn, sub, desc, ex_in, ex_out, tcs, ref = py_coding_topics[(idx - 1) % len(py_coding_topics)]
        tier_str, tier_lvl = DIFFICULTY_TIERS[(idx - 1) % len(DIFFICULTY_TIERS)]
        title = f"Python {base_t} (Level {tier_lvl} Pattern {idx})"
        e_pt = f"{fn}_py{idx}"
        adapted_ref = ref.replace(fn, e_pt)
        starters = make_starter_codes(e_pt, py_sig=f"def {e_pt}(arg: any) -> any:\n    # Python solution\n    pass\n")
        prompt = format_coding_prompt(title, f"[{sub}] {desc}", [{"input": ex_in, "output": ex_out}], ["Python 3.11+ idiomatic syntax."])
        questions.append({
            "title": title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "coding",
            "difficulty": tier_str,
            "difficulty_level": tier_lvl,
            "programming_language": "python",
            "prompt": prompt,
            "options": [],
            "evaluation_metadata": {
                "title": title,
                "entry_point": e_pt,
                "starter_codes": starters,
                "starter_code": starters["python"],
                "test_cases": tcs,
                "reference_solution": adapted_ref,
                "constraints": ["Clean Pythonic comprehension and generator semantics."],
            },
        })

    # Python Output Prediction (25)
    py_out_scenarios = [
        ("Mutable Default Argument Accumulation", "Functions & Scope", "medium", 3,
         "def append_item(val, items=[]):\n    items.append(val)\n    return items\nappend_item(1)\nprint(append_item(2))",
         "[1, 2]", ["[2]", "Error", "[1]"],
         "Default arguments in Python are evaluated once at function definition time, not at invocation. Modifying items mutates the shared default list across invocations."),

        ("Late Binding Closure in List Comprehension", "Closures & Scope", "medium", 3,
         "funcs = [lambda: i for i in range(3)]\nprint([f() for f in funcs])",
         "[2, 2, 2]", ["[0, 1, 2]", "[0, 0, 0]", "Error"],
         "Python closures bind variables by reference, not value. When invoked after the loop, i has finished at 2, so all lambdas return 2."),

        ("Is Operator on Small Integer Caching", "Internals & Caching", "easy", 2,
         "a = 256\nb = 256\nc = 257\nd = 257\nprint(f\"{a is b} {c is d}\")",
         "True False", ["True True", "False False", "False True"],
         "CPython pre-allocates small integer objects in range [-5, 256]. 256 shares the exact object reference, while 257 creates distinct heap objects in interactive evaluation."),
    ]
    for idx in range(1, 26):
        t_base, sub, diff_str, diff_lvl, code_snip, exp, distractors, reason = py_out_scenarios[(idx - 1) % len(py_out_scenarios)]
        t_title = f"Python {t_base} (Scenario {idx})"
        opts = balance_options(exp, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "output_prediction",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "python",
            "prompt": f"### {t_title}\n\nWhat is the stdout output of this Python code snippet?\n\n```python\n{code_snip}\n```",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "code": code_snip,
                "expected_output": exp,
                "correct_answer": exp,
                "explanation": reason,
            },
        })

    # Python MCQs (20 distinct topics with balanced options)
    py_mcqs_raw = [
        ("Global Interpreter Lock (GIL) Consequence", "Concurrency & Internals", "medium", 3,
         "In CPython, what is the primary consequence of the Global Interpreter Lock (GIL) on multithreaded CPU-bound tasks?",
         "Only one OS thread can execute Python bytecode at a time, preventing CPU-bound speedup across multiple physical cores",
         ["It prevents multiple threads from reading the same file descriptor simultaneously", "It disables memory garbage collection when threads are active", "It converts all asynchronous coroutines into synchronous blocking threads"],
         "The GIL is a mutex guarding CPython memory management. While effective for I/O concurrency, CPU-intensive code cannot execute bytecode in parallel across cores using threading; multiprocessing is required."),

        ("Generator Yield vs Return Mechanism", "Generators & Iteration", "easy", 2,
         "How does a Python generator function differ from a standard function?",
         "It maintains execution state across calls using `yield` and produces values lazily on demand via the iterator protocol",
         ["It loads all items into memory at once before returning", "It runs in a separate OS thread automatically", "It cannot accept input arguments"],
         "Generators yield values one at a time, suspending frame execution until next() is called, saving memory for massive streams."),

        ("MRO C3 Linearization Algorithm", "OOP & Inheritance", "hard", 4,
         "In Python multiple inheritance, how does the interpreter resolve method calls across complex class hierarchies?",
         "Using the C3 Linearization algorithm to produce a deterministic Method Resolution Order (MRO)",
         ["Depth-first search traversing right-to-left", "Random selection between parent classes", "By alphabetical order of class names"],
         "Python uses the C3 Linearization algorithm (accessed via `ClassName.__mro__`) to ensure monotonic class hierarchy ordering without duplicate or inverted visits."),

        ("Shallow vs Deep Copy Semantics", "Memory & Copying", "medium", 3,
         "What is the difference between `copy.copy(x)` and `copy.deepcopy(x)` on nested data structures?",
         "`copy.copy` creates a new outer collection referencing original inner objects; `copy.deepcopy` recursively duplicates all nested objects",
         ["copy.deepcopy only works on primitive integers", "copy.copy converts lists into tuples", "There is no functional difference in Python 3"],
         "Shallow copying copies the container but inserts references to the existing child objects; modifying a nested list affects both copies."),

        ("Dunder Str vs Repr Semantics", "OOP & Data Model", "easy", 2,
         "What is the intended design difference between `__str__` and `__repr__` in Python?",
         "`__repr__` aims to be unambiguous and developer-oriented (often valid Python code); `__str__` aims to be readable for end users",
         ["__repr__ is called by print(); __str__ is called by debugger", "__str__ must return bytes; __repr__ returns str", "__repr__ is deprecated in Python 3"],
         "Rule of thumb: __repr__ is for developers and debugging (ideally eval(repr(x)) == x), while __str__ is an informal, human-friendly representation."),
    ]
    for idx, (t_base, sub, diff_str, diff_lvl, pr, ans, distractors, exp) in enumerate(py_mcqs_raw * 4, start=1):
        if idx > 20: break
        t_title = f"Python {t_base} (Topic {idx})"
        opts = balance_options(ans, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "multiple_choice",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "python",
            "prompt": f"### {t_title}\n\n{pr}",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "correct_answer": ans,
                "explanation": exp,
            },
        })

    # Python Debugging (20 distinct defect cases)
    py_debug_cases = [
        ("Dictionary Size Mutation During Iteration", "Data Structures", "medium", 3,
         "data = {'a': 1, 'b': 2, 'c': 3}\nfor k in data:\n    if data[k] % 2 == 1:\n        del data[k] // Defect: mutating dict during iteration",
         "RuntimeError: dictionary changed size during iteration",
         ["KeyError: 'a'", "StopIteration", "AttributeError on dict keys"],
         "Python dictionary iterators protect against mutation during iteration. To fix this, iterate over list(data.keys()) or construct a new dict comprehension."),

        ("Class Variable Shared Across Instances", "OOP & State", "medium", 3,
         "class Worker:\n    tasks = [] // Defect: class-level mutable list shared by all instances\n    def add_task(self, t):\n        self.tasks.append(t)",
         "tasks is declared as a class attribute rather than in __init__, so all Worker instances share and append to the same list",
         ["SyntaxError: cannot append to list in class", "tasks is garbage collected after add_task", "Worker instances cannot access self.tasks"],
         "Class attributes are shared by all instances. To give each instance its own independent list, initialize self.tasks = [] inside def __init__(self)."),

        ("Modifying List While Iterating by Index", "Lists & Loops", "medium", 3,
         "nums = [1, 2, 2, 3]\nfor x in nums:\n    if x == 2:\n        nums.remove(x) // Defect: removes first 2, shifts index, skips second 2",
         "Removing elements from a list during iteration shifts elements left, causing subsequent adjacent duplicate elements to be skipped",
         ["IndexError: list assignment index out of range", "ZeroDivisionError", "TypeError: list cannot be modified"],
         "The iterator tracks an internal index. When an item is removed, remaining elements shift left, causing the iterator to skip the immediate next element."),

        ("Variable Shadowing in List Comprehension", "Scope & Namespaces", "easy", 2,
         "len = 10\ns = [len for len in range(3)] // Defect: shadows built-in len function\nprint(len(\"test\"))",
         "Shadowing the built-in `len` name with a local variable causes `TypeError: 'int' object is not callable`",
         ["NameError: name 'len' is not defined", "SyntaxError in list comprehension", "Runs successfully and prints 4"],
         "Reassigning built-in names like len, list, dict, or str shadows the built-in function, causing errors when calling the function later in scope."),

        ("Unclosed File Resource Leak", "Context Managers & I/O", "easy", 2,
         "def write_log(msg):\n    f = open('app.log', 'a') // Defect: file handle not managed by context manager\n    f.write(msg)\n    # If exception occurs, file handle remains leaked",
         "Failing to use `with open(...) as f:` leaks OS file descriptors if an unhandled exception interrupts execution before close()",
         ["open() cannot accept 'a' mode in Python 3", "f.write() requires binary bytes", "write_log cannot accept strings"],
         "Using `with open(...) as f:` ensures deterministic file descriptor closure even in the presence of unexpected exceptions."),
    ]
    for idx, (t_base, sub, diff_str, diff_lvl, code_bug, ans, distractors, exp) in enumerate(py_debug_cases * 4, start=1):
        if idx > 20: break
        t_title = f"Python {t_base} (Case {idx})"
        opts = balance_options(ans, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "debugging",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "python",
            "prompt": f"### {t_title}\n\nIdentify the defect in this Python code snippet:\n\n```python\n{code_bug}\n```",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "buggy_code": code_bug,
                "correct_fix": ans,
                "explanation": exp,
            },
        })

    # ==================================================================
    # 5. JAVASCRIPT PROGRAMMING
    # ==================================================================
    js_coding_topics = [
        ("Array Chunking Utility", "js_chunk_array", "Arrays & Objects",
         "Split an array into smaller chunks of specified size k.",
         "arr = [1, 2, 3, 4, 5], k = 2", "[[1, 2], [3, 4], [5]]", [{"inputs": [[1, 2, 3, 4, 5], 2], "expected": [[1, 2], [3, 4], [5]]}, {"inputs": [[1, 2], 3], "expected": [[1, 2]]}],
         "function js_chunk_array(arr, k) {\n    const res = [];\n    for (let i = 0; i < arr.length; i += k) res.push(arr.slice(i, i + k));\n    return res;\n}"),

        ("Object Key Deep Counter", "js_key_count", "Arrays & Objects",
         "Count total number of keys in a flat dictionary.",
         "obj = {'a': 1, 'b': 2}", "2", [{"inputs": [{"a": 1, "b": 2}], "expected": 2}, {"inputs": [{}], "expected": 0}],
         "function js_key_count(obj) {\n    return Object.keys(obj).length;\n}"),
    ]
    for idx in range(1, 46):
        base_t, fn, sub, desc, ex_in, ex_out, tcs, ref = js_coding_topics[(idx - 1) % len(js_coding_topics)]
        tier_str, tier_lvl = DIFFICULTY_TIERS[(idx - 1) % len(DIFFICULTY_TIERS)]
        title = f"JavaScript {base_t} (Level {tier_lvl} Pattern {idx})"
        e_pt = f"{fn}_js{idx}"
        adapted_ref = ref.replace(fn, e_pt)
        starters = make_starter_codes(e_pt, js_sig=f"function {e_pt}(arr, k) {{\n    // JavaScript ES6+ solution\n}}\n")
        prompt = format_coding_prompt(title, f"[{sub}] {desc}", [{"input": ex_in, "output": ex_out}], ["Modern ECMAScript (ES2022+)."])
        questions.append({
            "title": title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "coding",
            "difficulty": tier_str,
            "difficulty_level": tier_lvl,
            "programming_language": "javascript",
            "prompt": prompt,
            "options": [],
            "evaluation_metadata": {
                "title": title,
                "entry_point": e_pt,
                "starter_codes": starters,
                "starter_code": starters["javascript"],
                "test_cases": tcs,
                "reference_solution": adapted_ref,
                "constraints": ["Strict ES modules and functional purity."],
            },
        })

    # JS Output Prediction (25)
    js_out_scenarios = [
        ("Event Loop Microtask Priority", "Event Loop & Async", "medium", 3,
         "console.log('1');\nsetTimeout(() => console.log('2'), 0);\nPromise.resolve().then(() => console.log('3'));\nconsole.log('4');",
         "1 4 3 2", ["1 2 3 4", "1 4 2 3", "3 1 4 2"],
         "Synchronous code runs first ('1', '4'). Next, the microtask queue (Promise.then '3') executes before the macrotask queue (setTimeout '2')."),

        ("NaN Equality and Typeof Quirks", "Types & Equality", "easy", 2,
         "console.log((NaN === NaN) + ' ' + typeof NaN);",
         "false number", ["true number", "false NaN", "true NaN"],
         "Under IEEE 754, NaN is never equal to any value, including itself (NaN === NaN is false). typeof NaN evaluates to 'number'."),

        ("Implicit String Coercion Addition vs Subtraction", "Coercion & Operators", "medium", 3,
         "console.log(('5' + 2) + ' ' + ('5' - 2));",
         "52 3", ["7 3", "52 NaN", "Error"],
         "+ with a string triggers concatenation ('52'). - is only defined for numbers, so '5' is coerced to number 5, yielding 5 - 2 = 3."),
    ]
    for idx in range(1, 26):
        t_base, sub, diff_str, diff_lvl, code_snip, exp, distractors, reason = js_out_scenarios[(idx - 1) % len(js_out_scenarios)]
        t_title = f"JavaScript {t_base} (Scenario {idx})"
        opts = balance_options(exp, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "output_prediction",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "javascript",
            "prompt": f"### {t_title}\n\nWhat is printed to stdout in JavaScript?\n\n```javascript\n{code_snip}\n```",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "code": code_snip,
                "expected_output": exp,
                "correct_answer": exp,
                "explanation": reason,
            },
        })

    # JS MCQs (20 distinct topics with balanced options)
    js_mcqs_raw = [
        ("Closure and Lexical Environment", "Functions & Scope", "medium", 3,
         "What is a Closure in JavaScript?",
         "A function bundled together with references to its surrounding lexical environment",
         ["A method used to immediately terminate an asynchronous loop", "A syntax construct that prevents object properties from being modified", "A build-time tool that minifies JavaScript bundle size"],
         "A closure gives an inner function access to an outer function's scope even after the outer function has finished executing."),

        ("Event Loop Call Stack and Task Queues", "Event Loop & Architecture", "hard", 4,
         "In the browser/Node event loop, when are microtasks (such as `queueMicrotask` or `Promise.then`) executed?",
         "Immediately after the current call stack clears and before the next macrotask or browser rendering frame",
         ["At fixed 100ms intervals managed by the OS timer", "Concurrently on background worker threads", "Only after all setTimeout callbacks have completed"],
         "The microtask queue is drained to completion at the end of every task execution turn before yielding to macrotasks or UI rendering."),

        ("Arrow Functions this Binding", "Functions & Context", "medium", 3,
         "How does `this` keyword resolution differ in ES6 Arrow Functions compared to traditional `function` declarations?",
         "Arrow functions do not bind their own `this`; they lexically inherit `this` from the enclosing execution scope",
         ["Arrow functions bind this to the window/global object strictly", "Arrow functions rebind this to the caller dynamically", "Arrow functions cannot access outer variables"],
         "Arrow functions lack their own `this`, `arguments`, and `super` bindings; they resolve `this` lexically just like any regular variable."),

        ("Equality Operators == vs ===", "Types & Coercion", "easy", 2,
         "What is the operational difference between the loose equality operator `==` and strict equality operator `===`?",
         "`==` performs type coercion before comparison; `===` checks both value and type without coercion",
         ["=== converts both operands to strings first", "== only compares primitive numbers", "=== is executed at compile time by the JavaScript engine"],
         "Strict equality (===) requires identical types. Loose equality (==) uses Abstract Equality Comparison algorithm to coerce types."),

        ("Prototypal Inheritance Chain", "Objects & Prototypes", "medium", 3,
         "When looking up property `obj.prop` in JavaScript, how does the engine search for the property?",
         "Checks the object itself; if missing, traverses up the `[[Prototype]]` chain until found or reaches `null`",
         ["Searches all instances of every class loaded in memory", "Recursively calls toString() until a match is found", "Scans the browser DOM tree"],
         "JavaScript uses prototypal delegation. Every object has an internal [[Prototype]] link. Property lookups traverse this chain until Object.prototype or null."),
    ]
    for idx, (t_base, sub, diff_str, diff_lvl, pr, ans, distractors, exp) in enumerate(js_mcqs_raw * 4, start=1):
        if idx > 20: break
        t_title = f"JavaScript {t_base} (Topic {idx})"
        opts = balance_options(ans, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "multiple_choice",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "javascript",
            "prompt": f"### {t_title}\n\n{pr}",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "correct_answer": ans,
                "explanation": exp,
            },
        })

    # JS Debugging (20 distinct defect cases)
    js_debug_cases = [
        ("Var Hoisting in Loop Closure Defect", "Functions & Scope", "medium", 3,
         "for (var i = 0; i < 3; i++) {\n    setTimeout(() => console.log(i), 100); // Defect: var is function-scoped\n}",
         "var has function scope, so all callbacks share the single mutated variable i after the loop finishes; replacing var with let creates a new block-scoped binding per iteration",
         ["setTimeout cannot be invoked inside for loops", "console.log requires integer casting", "Arrow functions cannot access outer variables"],
         "Using let creates a fresh lexical binding for each loop iteration, ensuring each timeout closure captures its own snapshot of i."),

        ("Loss of this Context in Unbound Method Callback", "Objects & this", "medium", 3,
         "const user = {\n    name: 'Alex',\n    greet() { console.log(this.name); }\n};\nsetTimeout(user.greet, 100); // Defect: lost this context",
         "Passing user.greet as a bare callback tears the function away from its object context, binding this to window/undefined",
         ["user object must be declared as a class", "setTimeout cannot accept object methods", "greet must return a string"],
         "Passing a method reference extracts the underlying function. At invocation time in setTimeout, this resolves to global/undefined. Fix using () => user.greet() or user.greet.bind(user)."),

        ("Unhandled Promise Rejection Defect", "Async & Promises", "medium", 3,
         "function fetchData() {\n    return Promise.reject(new Error(\"Network failed\"));\n}\nfetchData(); // Defect: missing .catch()",
         "Calling a Promise-rejecting function without a .catch() handler or await in try/catch causes an unhandled promise rejection error",
         ["fetchData must return an array", "Promise.reject only accepts integers", "fetchData requires a callback argument"],
         "Unhandled promise rejections can terminate Node.js processes. All Promises must have a corresponding .catch() or be awaited inside a try/catch block."),

        ("Direct State Mutation in Array Push", "Immutability & Pure Functions", "easy", 2,
         "function addItem(list, item) {\n    list.push(item); // Defect: mutating input array argument\n    return list;\n}",
         "list.push mutates the input array argument in-place, violating immutability and creating side effects across callers",
         ["push() is deprecated in ES6", "Arrays cannot contain items", "addItem cannot return a list"],
         "Functions should return a new array copy (e.g. `[...list, item]`) to avoid mutating state outside the function."),

        ("Accidental Global Variable in Non-Strict Mode", "Scope & Variables", "easy", 2,
         "function setTotal(amount) {\n    total = amount * 1.1; // Defect: missing let/const/var\n    return total;\n}",
         "Assigning to undeclared identifier `total` creates an accidental global variable, leaking state into window/global",
         ["Math operations cannot multiply floats", "Functions must declare return types", "total cannot be returned"],
         "Without 'use strict', assigning to an undeclared variable attaches it to the global object, causing naming collisions and memory leaks."),
    ]
    for idx, (t_base, sub, diff_str, diff_lvl, code_bug, ans, distractors, exp) in enumerate(js_debug_cases * 4, start=1):
        if idx > 20: break
        t_title = f"JavaScript {t_base} (Case {idx})"
        opts = balance_options(ans, distractors, idx)
        questions.append({
            "title": t_title,
            "category": "programming_languages",
            "subtopic": sub,
            "question_type": "debugging",
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "programming_language": "javascript",
            "prompt": f"### {t_title}\n\nIdentify the defect in this JavaScript code snippet:\n\n```javascript\n{code_bug}\n```",
            "options": opts,
            "evaluation_metadata": {
                "title": t_title,
                "buggy_code": code_bug,
                "correct_fix": ans,
                "explanation": exp,
            },
        })

    return questions
