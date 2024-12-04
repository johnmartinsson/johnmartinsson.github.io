import os
import shutil
import jinja2
import yaml
from datetime import datetime, timezone

# Function to read a file's content
def read_file(filepath):
    with open(filepath, 'r') as file:
        return file.read()

# Load partials
head = read_file('templates/head.html')
header = read_file('templates/header.html')
footer = read_file('templates/footer.html')

# Set up Jinja2 environment
template_loader = jinja2.FileSystemLoader(searchpath="templates")
template_env = jinja2.Environment(loader=template_loader)

###############################################################################
# docs/index.html
###############################################################################

# Load the content file
content = read_file('content/index.html')

# Extract metadata and content
metadata, content = content.split('---', 2)[1:]
metadata = yaml.safe_load(metadata)

# Load the template
template = template_env.get_template('index.html')

# Render the template with metadata and content
rendered_html = template.render(title=metadata['title'], head=head, header=header, content=content, footer=footer)

# Save the rendered HTML to a file
output_path = os.path.join('docs', metadata['filename'])
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w') as file:
    file.write(rendered_html)

# Copy styles.css and script.js to the docs directory
shutil.copy('content/styles.css', 'docs/styles.css')
shutil.copy('content/script.js', 'docs/script.js')

# Copy images and audio directories to the docs directory
if os.path.exists('content/images'):
    shutil.copytree('content/images', 'docs/images', dirs_exist_ok=True)
if os.path.exists('content/audio'):
    shutil.copytree('content/audio', 'docs/audio', dirs_exist_ok=True)

print(f"Rendered HTML saved to {output_path}")

###############################################################################
# docs/blog.html
###############################################################################

# Function to load blog posts
def load_blog_posts(directory):
    posts = []
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            filepath = os.path.join(directory, filename)
            content = read_file(filepath)
            metadata, content = content.split('---', 2)[1:]
            metadata = yaml.safe_load(metadata)
            metadata['link'] = f"blog-posts/{filename}"
            metadata['content'] = content
            posts.append(metadata)
    # Sort posts by date (newest first)
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

# Load blog posts
posts = load_blog_posts('content/blog-posts')

# Render the blog page template with blog posts
blog_page_template = template_env.get_template('blog-page.html')
rendered_blog_page = blog_page_template.render(head=head, header=header, posts=posts, footer=footer)

# Save the rendered blog page to a file
output_blog_page_path = os.path.join('docs', 'blog.html')
os.makedirs(os.path.dirname(output_blog_page_path), exist_ok=True)
with open(output_blog_page_path, 'w') as file:
    file.write(rendered_blog_page)

# Render each blog post
for post in posts:
    post_template = template_env.get_template('index.html')
    rendered_post = post_template.render(title=post['title'], head=head, header=header, content=post['content'], footer=footer)
    output_post_path = os.path.join('docs', post['link'])
    os.makedirs(os.path.dirname(output_post_path), exist_ok=True)
    with open(output_post_path, 'w') as file:
        file.write(rendered_post)

print(f"Rendered blog page, and posts saved to {output_blog_page_path}")

# Generate RSS feed
rss_template = template_env.get_template('rss.xml')
rss_feed = rss_template.render(
    posts=posts,
    pub_date=datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000'),
    last_build_date=datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
)

# Save the RSS feed to a file
output_rss_path = os.path.join('docs', 'rss.xml')
with open(output_rss_path, 'w') as file:
    file.write(rss_feed)

print(f"Generated RSS feed saved to {output_rss_path}")