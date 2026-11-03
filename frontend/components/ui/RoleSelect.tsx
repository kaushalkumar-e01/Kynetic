"use client";

import { useState } from "react";
import { CAREER_TRACK_OPTIONS } from "./technologyCatalog";

interface RoleSelectProps {
  value: string;
  onChange: (val: string) => void;
  label?: string;
  placeholder?: string;
  required?: boolean;
}

export default function RoleSelect({
  value,
  onChange,
  label = "Target Career Role",
  placeholder = "Select or enter a target role...",
  required = false,
}: RoleSelectProps) {
  const [isCustom, setIsCustom] = useState(() => {
    return value ? !CAREER_TRACK_OPTIONS.includes(value) : false;
  });

  return (
    <div className="field">
      {label && <label>{label}</label>}
      <div style={{ display: "flex", gap: 8 }}>
        <select
          className="input"
          value={isCustom ? "custom" : value}
          onChange={(e) => {
            const val = e.target.value;
            if (val === "custom") {
              setIsCustom(true);
              onChange("");
            } else {
              setIsCustom(false);
              onChange(val);
            }
          }}
          required={required && !isCustom}
        >
          <option value="" disabled>
            {placeholder}
          </option>
          {CAREER_TRACK_OPTIONS.map((track) => (
            <option key={track} value={track}>
              {track}
            </option>
          ))}
          <option value="custom">-- Custom Role Title --</option>
        </select>
      </div>

      {isCustom && (
        <input
          type="text"
          className="input"
          style={{ marginTop: 8 }}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="e.g. Distributed Systems Infrastructure Engineer"
          required={required}
          autoFocus
        />
      )}
    </div>
  );
}
