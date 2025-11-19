"""
Customizable UI Themes for AAF

Provides CSS themes that can be embedded in any application.
Compatible with CopilotKit's theming system.
"""

from typing import Dict, Any, Optional


class AAFTheme:
    """
    AAF UI Theme configuration.
    
    Provides CSS variables that can be customized for any brand.
    """
    
    def __init__(
        self,
        name: str = "default",
        primary_color: str = "#6366f1",  # Indigo
        secondary_color: str = "#8b5cf6",  # Purple
        background_color: str = "#ffffff",
        text_color: str = "#1f2937",
        border_radius: str = "0.5rem",
        font_family: str = "system-ui, -apple-system, sans-serif"
    ):
        """
        Initialize theme.
        
        Args:
            name: Theme name
            primary_color: Primary brand color (hex)
            secondary_color: Secondary accent color (hex)
            background_color: Background color (hex)
            text_color: Text color (hex)
            border_radius: Border radius (CSS value)
            font_family: Font family (CSS value)
        """
        self.name = name
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.background_color = background_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.font_family = font_family
    
    def to_css_variables(self) -> str:
        """Generate CSS custom properties."""
        return f"""
:root {{
    /* AAF Theme: {self.name} */
    --aaf-primary-color: {self.primary_color};
    --aaf-secondary-color: {self.secondary_color};
    --aaf-background-color: {self.background_color};
    --aaf-text-color: {self.text_color};
    --aaf-border-radius: {self.border_radius};
    --aaf-font-family: {self.font_family};
    
    /* Derived colors */
    --aaf-primary-hover: color-mix(in srgb, {self.primary_color} 85%, black);
    --aaf-border-color: color-mix(in srgb, {self.text_color} 15%, transparent);
    --aaf-surface-color: color-mix(in srgb, {self.background_color} 98%, {self.text_color});
}}
"""
    
    def to_copilotkit_variables(self) -> str:
        """
        Generate CopilotKit-compatible CSS variables.
        
        This allows AAF themes to work with CopilotKit components.
        """
        return f"""
:root {{
    /* CopilotKit compatibility */
    --copilotkit-primary-color: {self.primary_color};
    --copilotkit-background-color: {self.background_color};
    --copilotkit-text-color: {self.text_color};
    --copilotkit-border-radius: {self.border_radius};
}}
"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Export as dictionary."""
        return {
            "name": self.name,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "background_color": self.background_color,
            "text_color": self.text_color,
            "border_radius": self.border_radius,
            "font_family": self.font_family
        }


# Pre-built themes
THEMES = {
    "default": AAFTheme(
        name="Default",
        primary_color="#6366f1",
        secondary_color="#8b5cf6"
    ),
    "dark": AAFTheme(
        name="Dark",
        primary_color="#818cf8",
        secondary_color="#a78bfa",
        background_color="#111827",
        text_color="#f9fafb"
    ),
    "ocean": AAFTheme(
        name="Ocean",
        primary_color="#0ea5e9",
        secondary_color="#06b6d4",
        background_color="#f0f9ff",
        text_color="#0c4a6e"
    ),
    "forest": AAFTheme(
        name="Forest",
        primary_color="#10b981",
        secondary_color="#059669",
        background_color="#f0fdf4",
        text_color="#064e3b"
    ),
    "sunset": AAFTheme(
        name="Sunset",
        primary_color="#f59e0b",
        secondary_color="#ef4444",
        background_color="#fffbeb",
        text_color="#78350f"
    ),
    "minimal": AAFTheme(
        name="Minimal",
        primary_color="#000000",
        secondary_color="#404040",
        background_color="#ffffff",
        text_color="#000000",
        border_radius="0.25rem"
    )
}


def get_theme(name: str = "default") -> AAFTheme:
    """Get theme by name."""
    return THEMES.get(name, THEMES["default"])


def generate_theme_css(theme_name: str = "default") -> str:
    """
    Generate complete CSS for a theme.
    
    Example:
        css = generate_theme_css("dark")
        # Include in HTML: <style>{css}</style>
    """
    theme = get_theme(theme_name)
    
    return f"""
{theme.to_css_variables()}
{theme.to_copilotkit_variables()}

/* AAF Component Styles */
.aaf-container {{
    font-family: var(--aaf-font-family);
    color: var(--aaf-text-color);
    background-color: var(--aaf-background-color);
}}

.aaf-chat-message {{
    padding: 1rem;
    border-radius: var(--aaf-border-radius);
    margin-bottom: 0.75rem;
}}

.aaf-chat-message.user {{
    background-color: var(--aaf-primary-color);
    color: white;
    margin-left: 2rem;
}}

.aaf-chat-message.assistant {{
    background-color: var(--aaf-surface-color);
    border: 1px solid var(--aaf-border-color);
    margin-right: 2rem;
}}

.aaf-button {{
    background-color: var(--aaf-primary-color);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: var(--aaf-border-radius);
    border: none;
    cursor: pointer;
    font-family: var(--aaf-font-family);
    transition: background-color 0.2s;
}}

.aaf-button:hover {{
    background-color: var(--aaf-primary-hover);
}}

.aaf-input {{
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--aaf-border-color);
    border-radius: var(--aaf-border-radius);
    font-family: var(--aaf-font-family);
    background-color: var(--aaf-background-color);
    color: var(--aaf-text-color);
}}

.aaf-card {{
    background-color: var(--aaf-surface-color);
    border: 1px solid var(--aaf-border-color);
    border-radius: var(--aaf-border-radius);
    padding: 1.5rem;
}}

.aaf-progress-bar {{
    width: 100%;
    height: 0.5rem;
    background-color: var(--aaf-border-color);
    border-radius: var(--aaf-border-radius);
    overflow: hidden;
}}

.aaf-progress-fill {{
    height: 100%;
    background-color: var(--aaf-primary-color);
    transition: width 0.3s ease;
}}

/* Code blocks */
.aaf-code {{
    background-color: color-mix(in srgb, var(--aaf-text-color) 5%, transparent);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-family: 'Monaco', 'Courier New', monospace;
    font-size: 0.875em;
}}

pre.aaf-code {{
    padding: 1rem;
    overflow-x: auto;
}}

/* Loading spinner */
.aaf-spinner {{
    border: 3px solid var(--aaf-border-color);
    border-top-color: var(--aaf-primary-color);
    border-radius: 50%;
    width: 2rem;
    height: 2rem;
    animation: aaf-spin 0.8s linear infinite;
}}

@keyframes aaf-spin {{
    to {{ transform: rotate(360deg); }}
}}
"""


def generate_html_embed(
    theme_name: str = "default",
    title: str = "AAF Agent",
    height: str = "600px"
) -> str:
    """
    Generate embeddable HTML widget.
    
    This can be iframe'd into any application.
    
    Example:
        html = generate_html_embed("dark", "My AI Assistant")
        # Save to file or serve via endpoint
    """
    css = generate_theme_css(theme_name)
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {css}
        body {{
            margin: 0;
            padding: 0;
            height: 100vh;
            overflow: hidden;
        }}
        #aaf-chat {{
            height: {height};
            display: flex;
            flex-direction: column;
        }}
        #messages {{
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
        }}
        #input-area {{
            padding: 1rem;
            border-top: 1px solid var(--aaf-border-color);
            background-color: var(--aaf-background-color);
        }}
    </style>
</head>
<body class="aaf-container">
    <div id="aaf-chat">
        <div id="messages"></div>
        <div id="input-area">
            <input 
                type="text" 
                id="user-input" 
                class="aaf-input" 
                placeholder="Ask me anything..."
            />
        </div>
    </div>
    
    <script>
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('user-input');
        
        function addMessage(role, content) {{
            const msg = document.createElement('div');
            msg.className = `aaf-chat-message ${{role}}`;
            msg.textContent = content;
            messagesDiv.appendChild(msg);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}
        
        input.addEventListener('keypress', async (e) => {{
            if (e.key === 'Enter' && input.value.trim()) {{
                const query = input.value.trim();
                addMessage('user', query);
                input.value = '';
                
                // Call AAF API
                try {{
                    const response = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ user_query: query }})
                    }});
                    const data = await response.json();
                    addMessage('assistant', data.response.message || JSON.stringify(data.response));
                }} catch (err) {{
                    addMessage('assistant', 'Error: ' + err.message);
                }}
            }}
        }});
        
        // Initial message
        addMessage('assistant', 'Hi! How can I help you today?');
    </script>
</body>
</html>
"""
