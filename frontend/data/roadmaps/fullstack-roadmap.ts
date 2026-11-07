import { CuratedRoadmap } from "./types";

export const fullstackRoadmap: CuratedRoadmap = {
  id: "full-stack",
  slug: "full-stack",
  title: "Full Stack Development",
  tagline: "Build end-to-end modern web applications: HTML/CSS, React, TypeScript, APIs, databases, and deployment.",
  description:
    "A complete, full-spectrum engineering pathway from web fundamentals and modern reactive user interfaces to scalable REST APIs, database persistence, JWT authentication, and cloud deployment pipelines.",
  category: "Web Development",
  difficulty: "Beginner",
  estimatedDuration: "16 - 20 weeks",
  badgeColor: "#10b981",
  phases: [
    {
      id: "fs-phase-1",
      order: 1,
      title: "Phase 1: Web Fundamentals, HTML5 & Modern CSS",
      description: "How the web works (HTTP/DNS), semantic markup, accessible design, Flexbox, and CSS Grid.",
      topics: [
        {
          id: "fs-internet-http",
          title: "How the Web Works: DNS, HTTP/HTTPS, Client-Server Architecture",
          shortDescription:
            "Understand domain name resolution, TCP/IP handshakes, SSL/TLS certificates, HTTP request/response methods, headers, and status codes.",
          learningObjectives: [
            "Trace what happens when typing a URL into a browser until bytes render",
            "Understand HTTP verbs (GET, POST, PUT, PATCH, DELETE) and status code families (2xx, 3xx, 4xx, 5xx)",
            "Inspect network traffic and headers using browser DevTools",
          ],
          prerequisites: ["None"],
          isEssential: true,
          resources: [
            {
              title: "MDN Web Docs - How the Web Works",
              url: "https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/How_the_Web_works",
              publisher: "MDN Web Docs",
              type: "article",
              isFree: true,
            },
            {
              title: "MDN Web Docs - An Overview of HTTP",
              url: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview",
              publisher: "MDN Web Docs",
              type: "documentation",
              isFree: true,
            },
          ],
        },
        {
          id: "fs-html5-semantic",
          title: "Semantic HTML5, Forms & Accessibility (WCAG / a11y)",
          shortDescription:
            "Structure content with semantic elements (<header>, <nav>, <main>, <article>), build validated forms, and use ARIA landmarks.",
          learningObjectives: [
            "Use semantic tags instead of generic <div> soup for search engines and screen readers",
            "Build accessible web forms with associated labels, validation attributes, and input types",
            "Audit accessibility using Lighthouse and adhere to WCAG contrast standards",
          ],
          prerequisites: ["fs-internet-http"],
          isEssential: true,
          resources: [
            {
              title: "MDN Web Docs - HTML: Structuring the Web",
              url: "https://developer.mozilla.org/en-US/docs/Learn/HTML",
              publisher: "MDN Web Docs",
              type: "tutorial",
              isFree: true,
            },
            {
              title: "W3Schools HTML5 Semantic Elements",
              url: "https://www.w3schools.com/html/html5_semantic_elements.asp",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "fs-css-modern-layouts",
          title: "Modern CSS: Flexbox, CSS Grid, Media Queries & Custom Properties",
          shortDescription:
            "Responsive layouts, 1D alignment with Flexbox, 2D layouts with Grid, mobile-first breakpoints, and CSS variables.",
          learningObjectives: [
            "Build dynamic 1D navigation and card rows using Flexbox (justify-content, align-items, flex-wrap)",
            "Construct complex 2D page scaffolding using CSS Grid (grid-template-columns, gap, repeat(auto-fit))",
            "Implement fluid typography and responsive designs with media queries and CSS custom properties",
          ],
          prerequisites: ["fs-html5-semantic"],
          isEssential: true,
          resources: [
            {
              title: "MDN Web Docs - Learn CSS",
              url: "https://developer.mozilla.org/en-US/docs/Learn/CSS",
              publisher: "MDN Web Docs",
              type: "tutorial",
              isFree: true,
            },
            {
              title: "A Complete Guide to Flexbox (CSS-Tricks)",
              url: "https://css-tricks.com/snippets/css/a-guide-to-flexbox/",
              publisher: "CSS-Tricks",
              type: "article",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "fs-phase-2",
      order: 2,
      title: "Phase 2: Modern JavaScript & TypeScript",
      description: "ES6+, DOM manipulation, asynchronous programming (promises, async/await), and TypeScript type safety.",
      topics: [
        {
          id: "fs-js-modern",
          title: "Modern JavaScript (ES6+), Closures, Event Loop & Async/Await",
          shortDescription:
            "Arrow functions, destructuring, spread/rest, promises, async/await, call stack, microtask queue, and fetch requests.",
          learningObjectives: [
            "Use let/const, arrow functions, template literals, and destructuring assignment",
            "Understand the JavaScript single-threaded event loop and asynchronous promise microtask queues",
            "Make asynchronous network requests using the Fetch API and handle error boundaries",
          ],
          prerequisites: ["fs-css-modern-layouts"],
          isEssential: true,
          resources: [
            {
              title: "javascript.info - The Modern JavaScript Tutorial",
              url: "https://javascript.info/",
              publisher: "javascript.info",
              type: "interactive",
              isFree: true,
            },
            {
              title: "MDN Web Docs - Asynchronous JavaScript",
              url: "https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous",
              publisher: "MDN Web Docs",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "fs-typescript-foundations",
          title: "TypeScript Essentials: Interfaces, Generics & Strict Typing",
          shortDescription:
            "Static typing for JavaScript, interface vs type aliases, union/intersection types, generics, and compiler options.",
          learningObjectives: [
            "Define data shapes with interfaces and custom type aliases",
            "Write reusable generic components and utility functions (T, K extends keyof T)",
            "Configure tsconfig.json with strict type checking enabled",
          ],
          prerequisites: ["fs-js-modern"],
          isEssential: true,
          resources: [
            {
              title: "TypeScript Official Handbook",
              url: "https://www.typescriptlang.org/docs/handbook/intro.html",
              publisher: "Microsoft TypeScript",
              type: "documentation",
              isFree: true,
            },
            {
              title: "W3Schools TypeScript Tutorial",
              url: "https://www.w3schools.com/typescript/",
              publisher: "W3Schools",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "fs-phase-3",
      order: 3,
      title: "Phase 3: React & Modern Frontend Architecture",
      description: "Component hierarchy, JSX, Hooks (useState, useEffect, useMemo), state lifting, and Next.js.",
      topics: [
        {
          id: "fs-react-hooks",
          title: "React Fundamentals: JSX, Props, State & Essential Hooks",
          shortDescription:
            "Declarative UI component trees, unidirectional data flow, useState, useEffect lifecycle, and event handlers.",
          learningObjectives: [
            "Structure clean component trees with typed props and modular JSX",
            "Manage local state with useState and handle side effects and cleanup with useEffect",
            "Lift state up to common parents and pass callbacks cleanly",
          ],
          prerequisites: ["fs-typescript-foundations"],
          isEssential: true,
          resources: [
            {
              title: "React Official Documentation - Describing the UI",
              url: "https://react.dev/learn",
              publisher: "React Docs",
              type: "documentation",
              isFree: true,
            },
            {
              title: "Full Stack Open - Deep Dive Into Modern Web Development",
              url: "https://fullstackopen.com/en/part1",
              publisher: "University of Helsinki",
              type: "interactive",
              isFree: true,
            },
          ],
        },
        {
          id: "fs-react-advanced-routing",
          title: "Global State Management, Routing & Next.js App Router",
          shortDescription:
            "Context API, routing paradigms, server components vs client components, and data fetching patterns.",
          learningObjectives: [
            "Provide global application context (theme, auth state) with React Context",
            "Build client-side multi-page routing and handle URL parameters",
            "Differentiate Server Components (fast initial load, zero client bundle) from Client Components ('use client')",
          ],
          prerequisites: ["fs-react-hooks"],
          isEssential: true,
          resources: [
            {
              title: "Next.js Official Documentation - App Router Guide",
              url: "https://nextjs.org/docs/app",
              publisher: "Vercel",
              type: "documentation",
              isFree: true,
            },
            {
              title: "React Official Docs - Managing State",
              url: "https://react.dev/learn/managing-state",
              publisher: "React Docs",
              type: "documentation",
              isFree: true,
            },
          ],
        },
      ],
    },
    {
      id: "fs-phase-4",
      order: 4,
      title: "Phase 4: Backend APIs, Databases & Authentication",
      description: "RESTful endpoints, middleware, database ORMs, JWT authentication, and CORS.",
      topics: [
        {
          id: "fs-backend-apis",
          title: "RESTful API Architecture & Backend Routing (Node.js/Express or FastAPI)",
          shortDescription:
            "Request lifecycle, URL routing, query parameters, request bodies, middleware chains, and centralized error handling.",
          learningObjectives: [
            "Design clean RESTful resource endpoints (/api/v1/resources)",
            "Validate incoming request schemas with Pydantic or Zod",
            "Implement middleware for request logging, CORS, and rate limiting",
          ],
          prerequisites: ["fs-react-advanced-routing"],
          isEssential: true,
          resources: [
            {
              title: "FastAPI Official Tutorial - User Guide",
              url: "https://fastapi.tiangolo.com/tutorial/",
              publisher: "FastAPI",
              type: "documentation",
              isFree: true,
            },
            {
              title: "MDN Express Tutorial - LocalLibrary Website",
              url: "https://developer.mozilla.org/en-US/docs/Learn/Server-side/Express_Nodejs",
              publisher: "MDN Web Docs",
              type: "tutorial",
              isFree: true,
            },
          ],
        },
        {
          id: "fs-auth-security",
          title: "Authentication, JWT Tokens, Password Hashing & OWASP Security",
          shortDescription:
            "Secure user authentication: bcrypt password hashing, JSON Web Tokens (access & refresh), HTTP-only cookies, and CORS protection.",
          learningObjectives: [
            "Hash and salt user passwords securely using bcrypt/argon2",
            "Sign, verify, and expire JWT bearer tokens for stateless auth",
            "Protect against XSS, CSRF, and SQL Injection adhering to OWASP Top 10 guidelines",
          ],
          prerequisites: ["fs-backend-apis"],
          isEssential: true,
          resources: [
            {
              title: "OWASP Top Ten Web Application Security Risks",
              url: "https://owasp.org/www-project-top-ten/",
              publisher: "OWASP Foundation",
              type: "documentation",
              isFree: true,
            },
            {
              title: "Auth0 JWT Introduction Guide",
              url: "https://jwt.io/introduction",
              publisher: "Auth0",
              type: "article",
              isFree: true,
            },
          ],
        },
        {
          id: "fs-deployment-devops",
          title: "Git, Containerization (Docker) & Cloud Deployment (Vercel/Render)",
          shortDescription:
            "Version control workflows, multi-stage Dockerfiles, environment variables (.env), and deploying full-stack apps to production.",
          learningObjectives: [
            "Manage feature branches, merges, and pull requests in Git",
            "Write a multi-stage Dockerfile to package web services into lightweight images",
            "Deploy frontend and backend applications with production environment secrets and SSL",
          ],
          prerequisites: ["fs-auth-security"],
          isEssential: false,
          resources: [
            {
              title: "Docker Get Started Guide",
              url: "https://docs.docker.com/get-started/",
              publisher: "Docker",
              type: "documentation",
              isFree: true,
            },
            {
              title: "Full Stack Open - Deploying Applications to the Cloud",
              url: "https://fullstackopen.com/en/part3/deploying_app_to_internet",
              publisher: "University of Helsinki",
              type: "interactive",
              isFree: true,
            },
          ],
        },
      ],
    },
  ],
};

