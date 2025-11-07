package com.markusgarantor.mooncode;

public class LuaFormatter {
    
    public static String format(String code) {
        if (code == null || code.isEmpty()) {
            return code;
        }

        StringBuilder formatted = new StringBuilder();
        String[] lines = code.split("\n");
        int indentLevel = 0;
        String indent = "    "; // 4 spaces

        for (String line : lines) {
            String trimmed = line.trim();
            
            // Decrease indent for end, else, elseif, until
            if (trimmed.startsWith("end") || trimmed.startsWith("else") || 
                trimmed.startsWith("elseif") || trimmed.startsWith("until")) {
                indentLevel = Math.max(0, indentLevel - 1);
            }

            // Add indentation
            for (int i = 0; i < indentLevel; i++) {
                formatted.append(indent);
            }
            formatted.append(trimmed).append("\n");

            // Increase indent for function, if, for, while, repeat, do
            if (trimmed.startsWith("function") || trimmed.startsWith("if") || 
                trimmed.startsWith("for") || trimmed.startsWith("while") || 
                trimmed.startsWith("repeat") || trimmed.endsWith("do") ||
                trimmed.startsWith("else") || trimmed.startsWith("elseif")) {
                indentLevel++;
            }

            // Decrease indent after end
            if (trimmed.startsWith("end")) {
                // Already decreased above
            }
        }

        return formatted.toString();
    }
}
