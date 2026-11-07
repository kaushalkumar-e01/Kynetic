import { CuratedRoadmap } from "./types";

export const mysqlRoadmap: CuratedRoadmap = {
  id: "mysql",
  slug: "mysql",
  title: "MySQL",
  tagline: "Master relational schema design, high-performance querying, B-tree indexes, and ACID transactions.",
  description:
    "A production-focused database curriculum taking you from foundational DDL/DML syntax and relational modeling to complex JOIN operations, query optimization with EXPLAIN, transaction isolation levels, and database normalization.",
  category: "Databases",
  difficulty: "Beginner",
  estimatedDuration: "6 - 8 weeks",
  badgeColor: "#00758f",
  phases: [
    {
      id: "mysql-phase-1",
      order: 1,
      title: "Phase 1: Relational Foundations & Core DDL / DML",
      description: "RDBMS architecture, schemas, tables, constraints, and standard CRUD operations.",
      topics: [
        {
          id: "mysql-rdbms-schema",
          title: "Relational Concepts, Data Types & Table Definition (DDL)",
          shortDescription:
            "Understand tables, rows, columns, character sets (utf8mb4), data types (INT, VARCHAR, DECIMAL, DATETIME), CREATE, ALTER, and DROP.",
          learningObjectives: [
            "Select optimal data types considering byte sizes and numeric precision",
            "Create schemas and tables using CREATE TABLE with sensible column defaults",
            "Perform non-destructive schema migrations using ALTER TABLE",
          ],
          prerequisites: ["None"],
          isEssential: true,
          resources: [
            {
              title: "MySQL 8.0 Reference Manual - Data Types",
              url: "https://dev.mysql.com/doc/refman/8.0/en/data-types.html",
              publisher: "Oracle MySQL",
              type: "documentation",
              isFree: true,
            },
            {
              title: "SQLBolt - Interactive SQL Lesson 1",
              url: "https://sqlbolt.com/lesson/introduction",
              publisher: "SQLBolt",
              type: "interactive",
              isFree: true,
            },
          ],
        },
        {
          id: "mysql-crud-queries",
          title: "Data Manipulation (DML): INSERT, SELECT, UPDATE, DELETE",
          shortDescription:
            "Standard CRUD operations, filtering with WHERE clauses, logical operators (AND, OR, NOT, IN, BETWEEN), and pattern matching (LIKE).",
          learningObjectives: [
            "Perform single-row and batch multi-row INSERTs",
            "Write safe UPDATE and DELETE queries with strict WHERE conditions to prevent table-wide corruption",
            "Use ORDER BY, LIMIT, and OFFSET for deterministic pagination",
          ],
          prerequisites: ["mysql-rdbms-schema"],
          isEssential: true,
          resources: [
            {
              title: "MySQL Tutorial - Basic SQL Queries",
              url: "https://www.mysqltutorial.org/mysql-basics/",
              publisher: "MySQLTutorial.org",
              type: "tutorial",
              isFree: true,
            },
            {
              title: "W3Schools MySQL Database Tutorial",
              url: "https://www.w3schools.com/mysql/default.asp",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "mysql-constraints-keys",
          title: "Integrity Constraints: PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL",
          shortDescription:
            "Enforce entity and referential integrity at the engine level, configure ON DELETE CASCADE vs ON DELETE RESTRICT.",
          learningObjectives: [
            "Design surrogate primary keys (AUTO_INCREMENT, UUIDs) and natural keys",
            "Enforce 1-to-Many and Many-to-Many foreign key constraints across tables",
            "Choose appropriate cascading actions (CASCADE, SET NULL, RESTRICT)",
          ],
          prerequisites: ["mysql-crud-queries"],
          isEssential: true,
          resources: [
            {
              title: "MySQL Docs - Using Foreign Key Constraints",
              url: "https://dev.mysql.com/doc/refman/8.0/en/create-table-foreign-keys.html",
              publisher: "Oracle MySQL",
              type: "documentation",
              isFree: true,
            },
            {
              title: "SQLBolt - Creating Tables and Constraints",
              url: "https://sqlbolt.com/lesson/creating_tables",
              publisher: "SQLBolt",
              type: "interactive",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "mysql-phase-2",
      order: 2,
      title: "Phase 2: Complex Joins, Aggregations & Subqueries",
      description: "Combining relational datasets, GROUP BY summaries, HAVING filters, and CTEs.",
      topics: [
        {
          id: "mysql-joins",
          title: "Relational Joins (INNER, LEFT, RIGHT, FULL & Self-Joins)",
          shortDescription:
            "Combine multi-table datasets via matching predicate keys, inspect Cartesian products, and handle NULL values in outer joins.",
          learningObjectives: [
            "Query matched records with INNER JOIN and handle partial matches with LEFT JOIN",
            "Simulate full outer joins using UNION of left and right joins",
            "Implement self-joins to query hierarchical data (e.g. employee-manager structures)",
          ],
          prerequisites: ["mysql-constraints-keys"],
          isEssential: true,
          resources: [
            {
              title: "SQLBolt - Multi-table queries with JOINs",
              url: "https://sqlbolt.com/lesson/select_queries_with_joins",
              publisher: "SQLBolt",
              type: "interactive",
              isFree: true,
            },
            {
              title: "MySQL Tutorial - Complete MySQL JOIN Guide",
              url: "https://www.mysqltutorial.org/mysql-join.aspx",
              publisher: "MySQLTutorial.org",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "mysql-aggregations",
          title: "Aggregations, GROUP BY, HAVING & Window Functions",
          shortDescription:
            "Summarize metrics with COUNT, SUM, AVG, MIN, MAX. Group datasets, filter groups with HAVING, and compute running totals.",
          learningObjectives: [
            "Distinguish between WHERE (row filter before aggregation) and HAVING (group filter after aggregation)",
            "Apply window functions (ROW_NUMBER(), RANK(), DENSE_RANK()) over partitions",
            "Avoid GROUP BY errors by adhering to ONLY_FULL_GROUP_BY SQL mode",
          ],
          prerequisites: ["mysql-joins"],
          isEssential: true,
          resources: [
            {
              title: "MySQL Docs - Aggregate Functions",
              url: "https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html",
              publisher: "Oracle MySQL",
              type: "documentation",
              isFree: true,
            },
            {
              title: "MySQL Tutorial - MySQL Window Functions",
              url: "https://www.mysqltutorial.org/mysql-window-functions/",
              publisher: "MySQLTutorial.org",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "mysql-subqueries-cte",
          title: "Subqueries, Common Table Expressions (CTEs) & Views",
          shortDescription:
            "Correlated vs non-correlated subqueries, readability improvements using WITH clauses (CTEs), and persistent virtual views.",
          learningObjectives: [
            "Write scalar and table-valued subqueries in WHERE and FROM clauses",
            "Use recursive and non-recursive Common Table Expressions (WITH cte AS ...)",
            "Create reusable SQL views to secure sensitive column projections",
          ],
          prerequisites: ["mysql-aggregations"],
          isEssential: false,
          resources: [
            {
              title: "MySQL Docs - WITH (Common Table Expressions)",
              url: "https://dev.mysql.com/doc/refman/8.0/en/with.html",
              publisher: "Oracle MySQL",
              type: "documentation",
              isFree: true,
            },
            {
              title: "MySQL Tutorial - MySQL Subquery",
              url: "https://www.mysqltutorial.org/mysql-subquery/",
              publisher: "MySQLTutorial.org",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "mysql-phase-3",
      order: 3,
      title: "Phase 3: Indexing, Query Optimization & Engine Internals",
      description: "B-Tree indexes, query execution plans (EXPLAIN), composite indexes, and schema design.",
      topics: [
        {
          id: "mysql-indexing-btree",
          title: "B-Tree Indexes, Clustered vs Secondary Indexes & Composite Keys",
          shortDescription:
            "How InnoDB structures tables around the clustered primary index, leaf pages, index lookups, and covering indexes.",
          learningObjectives: [
            "Explain how B-Trees enable O(log N) lookup and range scans",
            "Order composite index columns correctly following the leftmost-prefix rule",
            "Design covering indexes to eliminate secondary-to-primary lookup overhead",
          ],
          prerequisites: ["mysql-joins"],
          isEssential: true,
          resources: [
            {
              title: "Use The Index, Luke! - A Guide to Database Performance",
              url: "https://use-the-index-luke.com/",
              publisher: "Markus Winand",
              type: "interactive",
              isFree: true,
            },
            {
              title: "MySQL Docs - Optimization and Indexes",
              url: "https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html",
              publisher: "Oracle MySQL",
              type: "documentation",
              isFree: true,
            },
          ],
        },
        {
          id: "mysql-explain-tuning",
          title: "Query Profiling with EXPLAIN & Eliminating Full Table Scans",
          shortDescription:
            "Read EXPLAIN plans (type, possible_keys, key, rows, Extra like 'Using filesort' or 'Using temporary'), and refactor slow queries.",
          learningObjectives: [
            "Interpret access types: const, eq_ref, ref, range, index, and ALL (full scan)",
            "Detect and eliminate filesorts and temporary disk tables",
            "Refactor non-sargable WHERE predicates (e.g. functions wrapping indexed columns)",
          ],
          prerequisites: ["mysql-indexing-btree"],
          isEssential: true,
          resources: [
            {
              title: "MySQL Docs - Understanding the EXPLAIN Output Format",
              url: "https://dev.mysql.com/doc/refman/8.0/en/explain-output.html",
              publisher: "Oracle MySQL",
              type: "documentation",
              isFree: true,
            },
            {
              title: "MySQL Tutorial - MySQL EXPLAIN Explained",
              url: "https://www.mysqltutorial.org/mysql-explain/",
              publisher: "MySQLTutorial.org",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "mysql-phase-4",
      order: 4,
      title: "Phase 4: Transactions, Concurrency & Normalization",
      description: "ACID properties, InnoDB row-level locking, isolation levels, and normal forms.",
      topics: [
        {
          id: "mysql-acid-transactions",
          title: "ACID Properties & Transaction Control (START TRANSACTION, COMMIT, ROLLBACK)",
          shortDescription:
            "Guarantee data consistency: Atomicity, Consistency, Isolation, and Durability across multiple operations.",
          learningObjectives: [
            "Execute multi-statement transactions with proper rollback handling",
            "Understand write-ahead logging (redo log) and doublewrite buffering for crash safety",
            "Avoid long-running transactions that bloat undo logs",
          ],
          prerequisites: ["mysql-explain-tuning"],
          isEssential: true,
          resources: [
            {
              title: "MySQL Docs - InnoDB and the ACID Model",
              url: "https://dev.mysql.com/doc/refman/8.0/en/mysql-acid.html",
              publisher: "Oracle MySQL",
              type: "documentation",
              isFree: true,
            },
            {
              title: "MySQL Tutorial - MySQL Transaction Tutorial",
              url: "https://www.mysqltutorial.org/mysql-transaction.aspx",
              publisher: "MySQLTutorial.org",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "mysql-isolation-levels",
          title: "Transaction Isolation Levels & Concurrency Phenomena",
          shortDescription:
            "Read Uncommitted, Read Committed, Repeatable Read (MySQL default), and Serializable. Dirty reads, non-repeatable reads, and phantoms.",
          learningObjectives: [
            "Understand how MVCC (Multi-Version Concurrency Control) implements non-locking consistent reads",
            "Prevent deadlocks through consistent row lock acquisition ordering",
            "Use SELECT ... FOR UPDATE to implement pessimistic locking",
          ],
          prerequisites: ["mysql-acid-transactions"],
          isEssential: true,
          resources: [
            {
              title: "MySQL Docs - Transaction Isolation Levels",
              url: "https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html",
              publisher: "Oracle MySQL",
              type: "documentation",
              isFree: true,
            },
            {
              title: "GeeksforGeeks - Transaction Isolation Levels in DBMS",
              url: "https://www.geeksforgeeks.org/transaction-isolation-levels-in-dbms/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
          ],
        },
        {
          id: "mysql-normalization",
          title: "Database Normalization (1NF, 2NF, 3NF & BCNF)",
          shortDescription:
            "Eliminate data redundancy and update anomalies through functional dependencies and decomposition.",
          learningObjectives: [
            "Transform unnormalized tables into 1NF (atomic values, no repeating groups)",
            "Achieve 2NF (remove partial dependencies) and 3NF (remove transitive dependencies)",
            "Identify deliberate denormalization trade-offs for high-throughput read workloads",
          ],
          prerequisites: ["mysql-isolation-levels"],
          isEssential: false,
          resources: [
            {
              title: "GeeksforGeeks - Normal Forms in DBMS",
              url: "https://www.geeksforgeeks.org/normal-forms-in-dbms/",
              publisher: "GeeksforGeeks",
              type: "article",
              isFree: true,
            },
            {
              title: "W3Schools - Database Normalization",
              url: "https://www.w3schools.com/sql/sql_intro.asp",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
      ],
    },
  ],
};

