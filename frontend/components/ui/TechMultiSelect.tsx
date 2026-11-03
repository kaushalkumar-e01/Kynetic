"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import { Check, ChevronDown, Plus, Search, X } from "lucide-react";
import { TECHNOLOGY_CATALOG, type TechOption } from "./technologyCatalog";

interface TechMultiSelectProps {
  selected: string[];
  onChange: (selected: string[]) => void;
  placeholder?: string;
  label?: string;
  allowCustom?: boolean;
}

export default function TechMultiSelect({
  selected,
  onChange,
  placeholder = "Search and select technologies...",
  label,
  allowCustom = true,
}: TechMultiSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [customInput, setCustomInput] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleOption = (val: string) => {
    if (selected.includes(val)) {
      onChange(selected.filter((item) => item !== val));
    } else {
      onChange([...selected, val]);
    }
  };

  const removeOption = (val: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(selected.filter((item) => item !== val));
  };

  const handleAddCustom = (e: React.FormEvent) => {
    e.preventDefault();
    const clean = customInput.trim();
    if (!clean) return;
    if (!selected.includes(clean)) {
      onChange([...selected, clean]);
    }
    setCustomInput("");
  };

  const filteredOptions = useMemo(() => {
    const q = search.toLowerCase().trim();
    if (!q) return TECHNOLOGY_CATALOG;
    return TECHNOLOGY_CATALOG.filter(
      (opt) =>
        opt.label.toLowerCase().includes(q) ||
        opt.value.toLowerCase().includes(q) ||
        opt.category.toLowerCase().includes(q)
    );
  }, [search]);

  // Group filtered options by category
  const grouped = useMemo(() => {
    const map = new Map<string, TechOption[]>();
    for (const opt of filteredOptions) {
      if (!map.has(opt.category)) {
        map.set(opt.category, []);
      }
      map.get(opt.category)!.push(opt);
    }
    return map;
  }, [filteredOptions]);

  return (
    <div style={{ position: "relative" }} ref={dropdownRef}>
      {label && (
        <label style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 6, color: "var(--text)" }}>
          {label}
        </label>
      )}

      {/* Selected Items Chips + Trigger Bar */}
      <div
        onClick={() => setIsOpen((prev) => !prev)}
        style={{
          minHeight: 40,
          padding: "6px 12px",
          borderRadius: 8,
          background: "var(--surface)",
          border: `1px solid ${isOpen ? "var(--accent)" : "var(--line)"}`,
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 8,
          flexWrap: "wrap",
          transition: "border-color 0.2s ease",
        }}
      >
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, flex: 1, alignItems: "center" }}>
          {selected.length === 0 ? (
            <span className="muted" style={{ fontSize: 13 }}>
              {placeholder}
            </span>
          ) : (
            selected.map((val) => (
              <span
                key={val}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                  fontSize: 11,
                  padding: "2px 8px",
                  borderRadius: 4,
                  background: "rgba(0, 209, 178, 0.12)",
                  color: "var(--teal)",
                  border: "1px solid rgba(0, 209, 178, 0.3)",
                  fontWeight: 600,
                }}
              >
                {val}
                <button
                  type="button"
                  onClick={(e) => removeOption(val, e)}
                  style={{
                    background: "none",
                    border: "none",
                    padding: 0,
                    cursor: "pointer",
                    color: "inherit",
                    display: "flex",
                    alignItems: "center",
                  }}
                  title={`Remove ${val}`}
                >
                  <X size={11} />
                </button>
              </span>
            ))
          )}
        </div>
        <ChevronDown size={16} className="text-muted" style={{ transform: isOpen ? "rotate(180deg)" : "none", transition: "transform 0.2s" }} />
      </div>

      {/* Dropdown Panel */}
      {isOpen && (
        <div
          style={{
            position: "absolute",
            top: "calc(100% + 4px)",
            left: 0,
            right: 0,
            zIndex: 100,
            background: "var(--surface-2)",
            border: "1px solid var(--line)",
            borderRadius: 8,
            boxShadow: "0 10px 25px rgba(0,0,0,0.3)",
            maxHeight: 320,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          {/* Search Bar */}
          <div style={{ padding: "8px 10px", borderBottom: "1px solid var(--line)", display: "flex", alignItems: "center", gap: 8, background: "var(--surface)" }}>
            <Search size={14} className="text-muted" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search technologies, frameworks, tools..."
              onClick={(e) => e.stopPropagation()}
              style={{
                border: "none",
                background: "transparent",
                color: "var(--fg)",
                fontSize: 12,
                width: "100%",
                outline: "none",
              }}
              autoFocus
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch("")}
                style={{ background: "none", border: "none", cursor: "pointer", color: "var(--muted)", padding: 0 }}
              >
                <X size={12} />
              </button>
            )}
          </div>

          {/* Grouped Options List */}
          <div style={{ overflowY: "auto", flex: 1, padding: "6px 0" }}>
            {grouped.size === 0 ? (
              <div style={{ padding: "16px 12px", textAlign: "center", fontSize: 12, color: "var(--muted)" }}>
                No matching technologies found.
              </div>
            ) : (
              Array.from(grouped.entries()).map(([cat, options]) => (
                <div key={cat} style={{ marginBottom: 4 }}>
                  <div
                    style={{
                      padding: "4px 12px",
                      fontSize: 10,
                      fontWeight: 700,
                      textTransform: "uppercase",
                      color: "var(--muted)",
                      letterSpacing: "0.05em",
                    }}
                  >
                    {cat}
                  </div>
                  {options.map((opt) => {
                    const isSelected = selected.includes(opt.value);
                    return (
                      <div
                        key={opt.value}
                        onClick={() => toggleOption(opt.value)}
                        style={{
                          padding: "7px 12px",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          fontSize: 12,
                          cursor: "pointer",
                          background: isSelected ? "rgba(0, 209, 178, 0.08)" : "transparent",
                          color: isSelected ? "var(--teal)" : "var(--fg)",
                          transition: "background 0.15s ease",
                        }}
                        onMouseEnter={(e) => {
                          if (!isSelected) e.currentTarget.style.background = "var(--surface)";
                        }}
                        onMouseLeave={(e) => {
                          if (!isSelected) e.currentTarget.style.background = "transparent";
                        }}
                      >
                        <span>{opt.label}</span>
                        {isSelected && <Check size={14} color="var(--teal)" />}
                      </div>
                    );
                  })}
                </div>
              ))
            )}
          </div>

          {/* Custom "Other" Input */}
          {allowCustom && (
            <div
              style={{
                padding: "8px 10px",
                borderTop: "1px solid var(--line)",
                background: "var(--surface)",
                display: "flex",
                gap: 6,
                alignItems: "center",
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <input
                type="text"
                value={customInput}
                onChange={(e) => setCustomInput(e.target.value)}
                placeholder="Can't find it? Type custom technology..."
                style={{
                  flex: 1,
                  padding: "5px 8px",
                  borderRadius: 4,
                  border: "1px solid var(--line)",
                  background: "var(--surface-2)",
                  color: "var(--fg)",
                  fontSize: 11,
                  outline: "none",
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddCustom(e);
                  }
                }}
              />
              <button
                type="button"
                onClick={handleAddCustom}
                className="btn btn-outline"
                style={{ fontSize: 11, padding: "5px 8px" }}
                disabled={!customInput.trim()}
              >
                <Plus size={12} /> Add
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
