"""
Theme Customization Demo for AAF

Shows how to create custom themes and generate embeddable widgets
with different visual styles.
"""

import sys
sys.path.insert(0, '/home/runner/workspace')

from aaf.ui_themes import (
    AAFTheme,
    THEMES,
    get_theme,
    generate_theme_css,
    generate_html_embed
)


def demo_built_in_themes():
    """Show all built-in themes."""
    print("\n" + "="*70)
    print("Built-in AAF Themes")
    print("="*70)
    
    for name, theme in THEMES.items():
        print(f"\n📐 {theme.name} Theme")
        print(f"   Primary: {theme.primary_color}")
        print(f"   Secondary: {theme.secondary_color}")
        print(f"   Background: {theme.background_color}")
        print(f"   Text: {theme.text_color}")


def demo_custom_theme():
    """Create a custom brand theme."""
    print("\n" + "="*70)
    print("Custom Brand Theme")
    print("="*70)
    
    # Create custom theme for your brand
    my_theme = AAFTheme(
        name="MyBrand",
        primary_color="#ff6b6b",    # Coral red
        secondary_color="#4ecdc4",  # Teal
        background_color="#f7f7f7", # Light gray
        text_color="#2d3436",       # Dark gray
        border_radius="1rem",        # Rounded corners
        font_family="'Inter', sans-serif"
    )
    
    print(f"\n✅ Created custom theme: {my_theme.name}")
    print(f"   Colors: {my_theme.primary_color} / {my_theme.secondary_color}")
    
    # Generate CSS
    css = my_theme.to_css_variables()
    print(f"\n📝 CSS Variables generated ({len(css)} characters)")
    
    # Show first few lines
    print("\nPreview:")
    for line in css.split('\n')[:8]:
        print(f"  {line}")


def demo_copilotkit_compatibility():
    """Show CopilotKit compatibility."""
    print("\n" + "="*70)
    print("CopilotKit Compatibility")
    print("="*70)
    
    theme = get_theme("ocean")
    
    # Generate CopilotKit variables
    copilot_css = theme.to_copilotkit_variables()
    
    print("\n✅ AAF themes work with CopilotKit components!")
    print("\nGenerated CopilotKit CSS:")
    print(copilot_css)


def demo_html_widget():
    """Generate standalone HTML widget."""
    print("\n" + "="*70)
    print("Embeddable HTML Widget")
    print("="*70)
    
    # Generate widget with dark theme
    html = generate_html_embed(
        theme_name="dark",
        title="AAF AI Assistant",
        height="600px"
    )
    
    print(f"\n✅ Generated embeddable widget ({len(html)} bytes)")
    print("\nYou can:")
    print("  1. Save to HTML file")
    print("  2. Embed in iframe: <iframe src='widget.html' />")
    print("  3. Serve via FastAPI endpoint")
    print("  4. Customize theme by changing theme_name parameter")


def demo_all_theme_variations():
    """Show how different themes look."""
    print("\n" + "="*70)
    print("Theme Variations")
    print("="*70)
    
    themes_to_demo = ["default", "dark", "ocean", "forest", "sunset", "minimal"]
    
    for theme_name in themes_to_demo:
        theme = get_theme(theme_name)
        print(f"\n🎨 {theme.name} Theme")
        print(f"   Use case: ", end="")
        
        if theme_name == "default":
            print("General purpose, professional")
        elif theme_name == "dark":
            print("Night mode, developer tools")
        elif theme_name == "ocean":
            print("Analytics, data dashboards")
        elif theme_name == "forest":
            print("Health, sustainability apps")
        elif theme_name == "sunset":
            print("Creative, energetic apps")
        elif theme_name == "minimal":
            print("Clean, distraction-free")
        
        print(f"   Colors: {theme.primary_color} / {theme.secondary_color}")


def demo_css_generation():
    """Show complete CSS generation."""
    print("\n" + "="*70)
    print("Complete CSS Generation")
    print("="*70)
    
    # Generate complete CSS for sunset theme
    css = generate_theme_css("sunset")
    
    print(f"\n✅ Generated {len(css)} bytes of CSS")
    print("\nIncludes:")
    print("  • CSS custom properties")
    print("  • Component styles (buttons, inputs, cards)")
    print("  • Chat message bubbles")
    print("  • Progress bars")
    print("  • Code syntax highlighting")
    print("  • Loading spinners")
    print("  • Animations")
    
    # Save to file (optional)
    with open("/tmp/aaf_theme.css", "w") as f:
        f.write(css)
    
    print("\n📁 Saved to /tmp/aaf_theme.css")
    print("\nUsage:")
    print("  <link rel='stylesheet' href='aaf_theme.css'>")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("AAF Theme Customization Demo")
    print("="*70)
    print("\nMake AAF match your brand with custom themes!")
    
    demo_built_in_themes()
    demo_custom_theme()
    demo_copilotkit_compatibility()
    demo_html_widget()
    demo_all_theme_variations()
    demo_css_generation()
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print("""
AAF provides themeable UI that can be embedded anywhere:

✅ 6 built-in themes (default, dark, ocean, forest, sunset, minimal)
✅ Easy custom theme creation
✅ CopilotKit compatibility
✅ Embeddable HTML widgets
✅ Customizable CSS variables
✅ Works with any frontend framework

Integration options:
  1. React with CopilotKit (best for React apps)
  2. Standalone HTML widget (iframe embedding)
  3. Custom integration with generated CSS
  4. FastAPI endpoint serving themed UI

Next steps:
  • See examples/copilotkit_integration.tsx for React examples
  • Use generate_html_embed() for standalone widgets
  • Customize themes with AAFTheme class
  • Deploy embeddable widgets to your website
""")
    print("="*70 + "\n")
