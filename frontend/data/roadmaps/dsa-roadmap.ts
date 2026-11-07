import { CuratedRoadmap } from "./types";

export const dsaRoadmap: CuratedRoadmap = {
  id: "dsa",
  slug: "dsa",
  title: "Data Structures & Algorithms",
  tagline: "Master algorithmic problem-solving, asymptotic complexity analysis, and core data architectures.",
  description:
    "A rigorous, systematic path covering Big-O analysis, fundamental memory structures (arrays, linked lists, hash tables), non-linear hierarchies (trees, graphs), and advanced paradigm design (dynamic programming, greedy, divide-and-conquer).",
  category: "Computer Science",
  difficulty: "Intermediate",
  estimatedDuration: "12 - 16 weeks",
  badgeColor: "#8b5cf6",
  phases: [
    {
      id: "dsa-phase-1",
      order: 1,
      title: "Phase 1: Complexity Analysis & Linear Foundations",
      description: "Big-O notation, amortized analysis, dynamic arrays, two-pointer techniques, and sliding window.",
      topics: [
        {
          id: "dsa-complexity",
          title: "Asymptotic Analysis (Big-O, Omega, Theta & Space Complexity)",
          shortDescription:
            "Measure algorithmic scalability independently of hardware using growth orders (O(1), O(log n), O(n), O(n log n), O(n^2), O(2^n)).",
          learningObjectives: [
            "Compute tight upper (Big-O) and lower bounds for iterative loops and nested blocks",
            "Calculate auxiliary space complexity including call-stack overhead",
            "Understand amortized complexity (e.g. dynamic array resizing)",
          ],
          prerequisites: ["Basic algebra & programming loops"],
          isEssential: true,
          resources: [
            {
              title: "GeeksforGeeks - Analysis of Algorithms",
              url: "https://www.geeksforgeeks.org/analysis-of-algorithms-set-1-asymptotic-analysis/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
            {
              title: "FreeCodeCamp - Big O Notation Complete Guide",
              url: "https://www.freecodecamp.org/news/big-o-notation-why-it-matters-and-why-it-doesnt-1674cfa8a23c/",
              publisher: "freeCodeCamp",
              type: "article",
              isFree: true,
            },
          ],
        },
        {
          id: "dsa-arrays-strings",
          title: "Arrays, Strings, Two-Pointer & Sliding Window Techniques",
          shortDescription:
            "Contiguous memory operations, in-place array manipulation, opposite-direction pointers, and variable-length sliding windows.",
          learningObjectives: [
            "Apply the two-pointer pattern to solve sorted array search and partition problems in O(n) time and O(1) space",
            "Implement sliding window for maximum subarray sums and longest substring constraints",
            "Avoid common off-by-one errors and unnecessary auxiliary memory allocations",
          ],
          prerequisites: ["dsa-complexity"],
          isEssential: true,
          resources: [
            {
              title: "NeetCode Roadmap - Arrays & Hashing",
              url: "https://neetcode.io/roadmap",
              publisher: "NeetCode",
              type: "interactive",
              isFree: true,
            },
            {
              title: "W3Schools DSA - Arrays Tutorial",
              url: "https://www.w3schools.com/dsa/dsa_theory_arrays.php",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "dsa-hash-tables",
          title: "Hash Tables, Collision Resolution & Amortized O(1) Lookups",
          shortDescription:
            "Hash functions, separate chaining, open addressing (linear/quadratic probing), load factors, and frequency maps.",
          learningObjectives: [
            "Explain how hash functions map arbitrary keys into bucket indices",
            "Analyze worst-case O(n) degradation under hash collisions and load factor thresholds",
            "Use hash maps and hash sets to reduce O(n^2) nested lookups to linear O(n)",
          ],
          prerequisites: ["dsa-arrays-strings"],
          isEssential: true,
          resources: [
            {
              title: "VisuAlgo - Hash Table Interactive Visualization",
              url: "https://visualgo.net/en/hashtable",
              publisher: "VisuAlgo",
              type: "interactive",
              isFree: true,
            },
            {
              title: "GeeksforGeeks - Hashing Data Structure",
              url: "https://www.geeksforgeeks.org/hashing-data-structure/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "dsa-phase-2",
      order: 2,
      title: "Phase 2: Linked Lists, Stacks, Queues & Heaps",
      description: "Pointer-linked nodes, LIFO/FIFO patterns, monotonic stacks, and priority queues.",
      topics: [
        {
          id: "dsa-linked-lists",
          title: "Linked Lists (Singly, Doubly) & Fast/Slow Pointer Pattern",
          shortDescription:
            "Non-contiguous node chains, dynamic insertion/deletion without resizing, cycle detection with Floyd's tortoise and hare.",
          learningObjectives: [
            "Implement singly and doubly linked lists with dummy head nodes",
            "Reverse a linked list iteratively in O(n) time and O(1) space",
            "Detect and locate cycle entrance points using Floyd's two-pointer algorithm",
          ],
          prerequisites: ["dsa-arrays-strings"],
          isEssential: true,
          resources: [
            {
              title: "VisuAlgo - Linked List Visualization",
              url: "https://visualgo.net/en/list",
              publisher: "VisuAlgo",
              type: "interactive",
              isFree: true,
            },
            {
              title: "W3Schools DSA - Linked Lists",
              url: "https://www.w3schools.com/dsa/dsa_theory_linkedlists.php",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "dsa-stacks-queues",
          title: "Stacks, Queues, Deques & Monotonic Stack Patterns",
          shortDescription:
            "LIFO and FIFO execution, circular buffers, balanced parentheses validation, and next-greater-element monotonic scans.",
          learningObjectives: [
            "Implement stack and queue interfaces using array buffers and linked nodes",
            "Validate nested syntax brackets using a stack in O(n) time",
            "Use monotonic increasing/decreasing stacks to solve histogram and next-greater element problems",
          ],
          prerequisites: ["dsa-linked-lists"],
          isEssential: true,
          resources: [
            {
              title: "GeeksforGeeks - Stack Data Structure",
              url: "https://www.geeksforgeeks.org/stack-data-structure/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
            {
              title: "VisuAlgo - Queue & Stack Visualizer",
              url: "https://visualgo.net/en/list",
              publisher: "VisuAlgo",
              type: "interactive",
              isFree: true,
            },
          ],
        },
        {
          id: "dsa-heaps-priority-queues",
          title: "Binary Heaps & Priority Queues",
          shortDescription:
            "Complete binary trees stored in contiguous arrays, min-heap/max-heap invariant, heapify in O(n), and O(log n) pop/push.",
          learningObjectives: [
            "Represent binary heaps in 1-based or 0-based arrays (parent = (i-1)/2, children = 2i+1, 2i+2)",
            "Perform sift-up and sift-down operations maintaining the heap property",
            "Solve Top-K elements and median-stream tracking problems with heaps",
          ],
          prerequisites: ["dsa-stacks-queues"],
          isEssential: true,
          resources: [
            {
              title: "VisuAlgo - Binary Heap Visualizer",
              url: "https://visualgo.net/en/heap",
              publisher: "VisuAlgo",
              type: "interactive",
              isFree: true,
            },
            {
              title: "GeeksforGeeks - Binary Heap Tutorial",
              url: "https://www.geeksforgeeks.org/binary-heap/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "dsa-phase-3",
      order: 3,
      title: "Phase 3: Hierarchical Structures (Trees & Graphs)",
      description: "Binary Search Trees, BFS, DFS, shortest path algorithms, and topological sorting.",
      topics: [
        {
          id: "dsa-trees-traversals",
          title: "Binary Trees & Tree Traversals (Inorder, Preorder, Postorder, BFS Level-Order)",
          shortDescription:
            "Recursive and iterative tree processing, depth-first visits, breadth-first level-by-level queue traversals, and maximum depth.",
          learningObjectives: [
            "Implement recursive and stack-based iterative traversals",
            "Use queue-based BFS to process nodes level by level",
            "Compute tree height, diameter, and subtree isomorphisms",
          ],
          prerequisites: ["dsa-heaps-priority-queues"],
          isEssential: true,
          resources: [
            {
              title: "VisuAlgo - Binary Search Tree Visualization",
              url: "https://visualgo.net/en/bst",
              publisher: "VisuAlgo",
              type: "interactive",
              isFree: true,
            },
            {
              title: "W3Schools DSA - Binary Trees",
              url: "https://www.w3schools.com/dsa/dsa_theory_trees.php",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "dsa-graphs-traversal",
          title: "Graph Representations, Breadth-First Search (BFS) & Depth-First Search (DFS)",
          shortDescription:
            "Adjacency lists vs adjacency matrices, visited tracking, connected components, cycle detection, and shortest unweighted paths.",
          learningObjectives: [
            "Construct memory-efficient adjacency lists for directed and undirected graphs",
            "Use BFS to find shortest path in unweighted graphs in O(V + E)",
            "Detect cycles in directed graphs using three-color DFS (white/gray/black)",
          ],
          prerequisites: ["dsa-trees-traversals"],
          isEssential: true,
          resources: [
            {
              title: "VisuAlgo - Graph Traversal (DFS/BFS)",
              url: "https://visualgo.net/en/dfsbfs",
              publisher: "VisuAlgo",
              type: "interactive",
              isFree: true,
            },
            {
              title: "GeeksforGeeks - Graph Data Structure & Algorithms",
              url: "https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
          ],
        },
        {
          id: "dsa-graphs-advanced",
          title: "Dijkstra's Algorithm, Topological Sort & Disjoint Set Union (DSU)",
          shortDescription:
            "Weighted shortest paths using priority queues, Kahn's algorithm / DFS for DAG task scheduling, and union-by-rank with path compression.",
          learningObjectives: [
            "Implement Dijkstra's algorithm for non-negative weighted graphs in O((V + E) log V)",
            "Order prerequisites and build steps with Topological Sort",
            "Manage dynamic partitions with Disjoint Set Union (Union-Find)",
          ],
          prerequisites: ["dsa-graphs-traversal"],
          isEssential: true,
          resources: [
            {
              title: "VisuAlgo - Single-Source Shortest Paths (Dijkstra)",
              url: "https://visualgo.net/en/sssp",
              publisher: "VisuAlgo",
              type: "interactive",
              isFree: true,
            },
            {
              title: "GeeksforGeeks - Disjoint Set (Union-Find) Algorithm",
              url: "https://www.geeksforgeeks.org/introduction-to-disjoint-set-data-structure-or-union-find-algorithm/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "dsa-phase-4",
      order: 4,
      title: "Phase 4: Algorithmic Paradigms & Dynamic Programming",
      description: "Binary search, merge/quick sort, greedy strategies, 1D/2D dynamic programming.",
      topics: [
        {
          id: "dsa-sorting-searching",
          title: "Binary Search, Merge Sort & Quick Sort",
          shortDescription:
            "Divide and conquer: O(n log n) sorting guarantees, stability, in-place partitioning, and binary search on monotonic answer spaces.",
          learningObjectives: [
            "Implement iterative binary search without integer overflow (low + (high - low) / 2)",
            "Code Merge Sort recursively and analyze its O(n) auxiliary space",
            "Write Quick Sort with Lomuto or Hoare partitioning schemes",
          ],
          prerequisites: ["dsa-graphs-traversal"],
          isEssential: true,
          resources: [
            {
              title: "VisuAlgo - Comparison Sorting Algorithms",
              url: "https://visualgo.net/en/sorting",
              publisher: "VisuAlgo",
              type: "interactive",
              isFree: true,
            },
            {
              title: "GeeksforGeeks - Binary Search Tutorial",
              url: "https://www.geeksforgeeks.org/binary-search/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
          ],
        },
        {
          id: "dsa-dynamic-programming",
          title: "Dynamic Programming (Memoization vs Tabulation, 1D & 2D)",
          shortDescription:
            "Optimal substructure and overlapping subproblems: top-down recursive caching, bottom-up DP tables, and state transitions.",
          learningObjectives: [
            "Identify DP patterns: 0/1 Knapsack, Longest Common Subsequence (LCS), Longest Increasing Subsequence (LIS)",
            "Formulate recurrence relations and base conditions",
            "Optimize 2D DP space down to 1D rolling arrays",
          ],
          prerequisites: ["dsa-sorting-searching"],
          isEssential: true,
          resources: [
            {
              title: "FreeCodeCamp - Dynamic Programming Complete Course",
              url: "https://www.freecodecamp.org/news/learn-dynamic-programing-to-solve-coding-challenges/",
              publisher: "freeCodeCamp",
              type: "tutorial",
              isFree: true,
            },
            {
              title: "GeeksforGeeks - Dynamic Programming",
              url: "https://www.geeksforgeeks.org/dynamic-programming/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
          ],
        },
      ],
    },
  ],
};

