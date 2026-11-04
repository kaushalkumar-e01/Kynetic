export interface TechOption {
  value: string;
  label: string;
  category: "Languages" | "Frontend" | "Backend" | "Mobile" | "Databases" | "DevOps & Cloud" | "Concepts & Tools";
}

export const TECHNOLOGY_CATALOG: TechOption[] = [
  // Programming Languages
  { value: "Python", label: "Python", category: "Languages" },
  { value: "JavaScript", label: "JavaScript", category: "Languages" },
  { value: "TypeScript", label: "TypeScript", category: "Languages" },
  { value: "Java", label: "Java", category: "Languages" },
  { value: "C++", label: "C++", category: "Languages" },
  { value: "C#", label: "C#", category: "Languages" },
  { value: "C", label: "C", category: "Languages" },
  { value: "Go", label: "Go (Golang)", category: "Languages" },
  { value: "Rust", label: "Rust", category: "Languages" },
  { value: "SQL", label: "SQL", category: "Languages" },
  { value: "PHP", label: "PHP", category: "Languages" },
  { value: "Ruby", label: "Ruby", category: "Languages" },
  { value: "Kotlin", label: "Kotlin", category: "Languages" },
  { value: "Swift", label: "Swift", category: "Languages" },
  { value: "Dart", label: "Dart", category: "Languages" },

  // Frontend Frameworks & Libraries
  { value: "React", label: "React", category: "Frontend" },
  { value: "Next.js", label: "Next.js", category: "Frontend" },
  { value: "Vue", label: "Vue.js", category: "Frontend" },
  { value: "Angular", label: "Angular", category: "Frontend" },
  { value: "Svelte", label: "Svelte", category: "Frontend" },
  { value: "Tailwind CSS", label: "Tailwind CSS", category: "Frontend" },
  { value: "HTML5", label: "HTML5", category: "Frontend" },
  { value: "CSS3", label: "CSS3", category: "Frontend" },
  { value: "Redux", label: "Redux / Redux Toolkit", category: "Frontend" },
  { value: "Zustand", label: "Zustand", category: "Frontend" },

  // Backend Frameworks & Libraries
  { value: "FastAPI", label: "FastAPI", category: "Backend" },
  { value: "Node.js", label: "Node.js", category: "Backend" },
  { value: "Express", label: "Express.js", category: "Backend" },
  { value: "Django", label: "Django", category: "Backend" },
  { value: "Flask", label: "Flask", category: "Backend" },
  { value: "Spring Boot", label: "Spring Boot", category: "Backend" },
  { value: "NestJS", label: "NestJS", category: "Backend" },
  { value: "ASP.NET Core", label: "ASP.NET Core", category: "Backend" },
  { value: "Ruby on Rails", label: "Ruby on Rails", category: "Backend" },
  { value: "Laravel", label: "Laravel", category: "Backend" },

  // Mobile
  { value: "React Native", label: "React Native", category: "Mobile" },
  { value: "Flutter", label: "Flutter", category: "Mobile" },
  { value: "Android SDK", label: "Android SDK", category: "Mobile" },
  { value: "SwiftUI", label: "SwiftUI / iOS", category: "Mobile" },

  // Databases & Caching
  { value: "PostgreSQL", label: "PostgreSQL", category: "Databases" },
  { value: "MySQL", label: "MySQL", category: "Databases" },
  { value: "SQLite", label: "SQLite", category: "Databases" },
  { value: "MongoDB", label: "MongoDB", category: "Databases" },
  { value: "Redis", label: "Redis", category: "Databases" },
  { value: "Supabase", label: "Supabase", category: "Databases" },
  { value: "Firebase", label: "Firebase / Firestore", category: "Databases" },
  { value: "Elasticsearch", label: "Elasticsearch", category: "Databases" },

  // DevOps, Cloud & Infrastructure
  { value: "Docker", label: "Docker", category: "DevOps & Cloud" },
  { value: "Kubernetes", label: "Kubernetes", category: "DevOps & Cloud" },
  { value: "AWS", label: "AWS (Amazon Web Services)", category: "DevOps & Cloud" },
  { value: "GCP", label: "Google Cloud Platform", category: "DevOps & Cloud" },
  { value: "Azure", label: "Microsoft Azure", category: "DevOps & Cloud" },
  { value: "Git", label: "Git", category: "DevOps & Cloud" },
  { value: "GitHub Actions", label: "GitHub Actions (CI/CD)", category: "DevOps & Cloud" },
  { value: "Linux", label: "Linux / Unix Administration", category: "DevOps & Cloud" },
  { value: "Terraform", label: "Terraform", category: "DevOps & Cloud" },

  // Core Concepts & Tools
  { value: "REST API", label: "RESTful API Design", category: "Concepts & Tools" },
  { value: "GraphQL", label: "GraphQL", category: "Concepts & Tools" },
  { value: "Microservices", label: "Microservices Architecture", category: "Concepts & Tools" },
  { value: "Data Structures", label: "Data Structures & Algorithms", category: "Concepts & Tools" },
  { value: "System Design", label: "System Design & Scalability", category: "Concepts & Tools" },
  { value: "Machine Learning", label: "Machine Learning", category: "Concepts & Tools" },
  { value: "Pytest", label: "Pytest / Unit Testing", category: "Concepts & Tools" },
  { value: "Jest", label: "Jest / Vitest", category: "Concepts & Tools" },
];

export const ALL_TECHNOLOGIES: string[] = TECHNOLOGY_CATALOG.map((t) => t.value);

export const CAREER_TRACK_OPTIONS = [
  "Backend Platform Engineer",
  "Frontend Web Engineer",
  "Full Stack Software Engineer",
  "Data Scientist / ML Engineer",
  "DevOps & Cloud Infrastructure Engineer",
  "Mobile Application Engineer",
  "Security & Systems Engineer",
  "QA & Test Automation Engineer",
  "AI Systems / LLM Applications Engineer",
];
