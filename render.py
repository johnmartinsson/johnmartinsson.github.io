import os
import shutil
import jinja2
import yaml

# Load the content file
with open('content/index.html', 'r') as file:
    content = file.read()

# Extract metadata and content
metadata, content = content.split('---', 2)[1:]
metadata = yaml.safe_load(metadata)

# Set up Jinja2 environment
template_loader = jinja2.FileSystemLoader(searchpath="templates")
template_env = jinja2.Environment(loader=template_loader)

# Load the template
template = template_env.get_template('index.html')

# Render the template with metadata and content
rendered_html = template.render(title=metadata['title'], content=content)

# Save the rendered HTML to a file
output_path = os.path.join('output', metadata['filename'])
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w') as file:
    file.write(rendered_html)

# Copy styles.css and script.js to the output directory
shutil.copy('styles.css', 'output/styles.css')
shutil.copy('script.js', 'output/script.js')

# Copy images and audio directories to the output directory
if os.path.exists('images'):
    shutil.copytree('images', 'output/images', dirs_exist_ok=True)
if os.path.exists('audio'):
    shutil.copytree('audio', 'output/audio', dirs_exist_ok=True)

print(f"Rendered HTML saved to {output_path}")