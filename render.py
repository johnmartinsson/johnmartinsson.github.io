import os
import shutil
import jinja2
import yaml
from datetime import datetime, timezone

from csscompressor import compress
from jsmin import jsmin
from PIL import Image
import subprocess


# Function to convert images to WebP and resize them
def convert_images_to_webp(src_dir, dest_dir, max_width=800):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith(('png', 'jpg', 'jpeg')):
                src_path = os.path.join(root, file)
                dest_path = os.path.join(dest_dir, os.path.relpath(root, src_dir), os.path.splitext(file)[0] + '.webp')
                if not os.path.exists(dest_path):
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    with Image.open(src_path) as img:
                        # Resize image if it exceeds max_width
                        if img.width > max_width:
                            ratio = max_width / float(img.width)
                            new_height = int((float(img.height) * float(ratio)))
                            img = img.resize((max_width, new_height), Image.LANCZOS)
                        img.save(dest_path, 'webp')

# Function to convert audio files to WebM
def convert_audio_to_webm(src_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith(('mp3', 'wav')):
                src_path = os.path.join(root, file)
                dest_path = os.path.join(dest_dir, os.path.relpath(root, src_dir), os.path.splitext(file)[0] + '.webm')
                if not os.path.exists(dest_path):
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    subprocess.run(['ffmpeg', '-i', src_path, '-b:a', '64k', dest_path])

# Function to read a file's content
def read_file(filepath):
    with open(filepath, 'r') as file:
        return file.read()

# Load partials
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
head_template = template_env.get_template('head.html')
template = template_env.get_template('index.html')

# Render the template with metadata and content
rendered_html = template.render(
    title=metadata['title'], 
    head=head_template.render(meta_title=metadata['title'], meta_description=metadata['description']), 
    header=header, 
    content=content, 
    footer=footer
)

# Save the rendered HTML to a file
output_path = os.path.join('docs', metadata['filename'])
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w') as file:
    file.write(rendered_html)

# Minify and copy styles.css and script.js to the docs directory
css_content = read_file('content/styles.css')
minified_css = compress(css_content)
with open('docs/styles.css', 'w') as file:
    file.write(minified_css)

js_content = read_file('content/script.js')
minified_js = jsmin(js_content)
with open('docs/script.js', 'w') as file:
    file.write(minified_js)


# Convert images to WebP and copy to the docs directory
convert_images_to_webp('content/images', 'docs/images')

# Convert audio files to WebM and copy to the docs directory
convert_audio_to_webm('content/audio', 'docs/audio')

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
            metadata['link'] = f"blog/{filename}"
            metadata['content'] = content
            # Ensure the date is a string before parsing
            if isinstance(metadata['date'], datetime):
                metadata['date'] = metadata['date'].strftime('%Y-%m-%d')
            posts.append(metadata)
    # Sort posts by date (newest first)
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

# Load blog posts
posts = load_blog_posts('content/blog')

# Render the blog page template with blog posts
blog_page_template = template_env.get_template('blog-page.html')
rendered_blog_page = blog_page_template.render(
    head=head_template.render(meta_title="John Martinsson's Blog", meta_description="Updates and blog posts about John Martinsson's work in bioacoustics and machine listening."),
    header=header, 
    posts=posts, 
    footer=footer
)

# Save the rendered blog page to a file
output_blog_page_path = os.path.join('docs', 'blog.html')
os.makedirs(os.path.dirname(output_blog_page_path), exist_ok=True)
with open(output_blog_page_path, 'w') as file:
    file.write(rendered_blog_page)

# Render each blog post
for post in posts:
    post_template = template_env.get_template('index.html')
    rendered_post = post_template.render(
        title=post['title'], 
        head=head_template.render(meta_title=post['title'], meta_description=post['description']),
        header=header, 
        content=post['content'], 
        footer=footer
    )
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

# Generate sitemap
sitemap_template = template_env.get_template('sitemap.xml')
sitemap = sitemap_template.render(
    posts=posts,
    lastmod=datetime.now(timezone.utc).strftime('%Y-%m-%d')
)

# Save the sitemap to a file
output_sitemap_path = os.path.join('docs', 'sitemap.xml')
with open(output_sitemap_path, 'w') as file:
    file.write(sitemap)

print(f"Generated sitemap saved to {output_sitemap_path}")

# Copy robots.txt to the docs directory
shutil.copy('content/robots.txt', 'docs/robots.txt')


# Function to resize favicon.ico to 32x32 pixels
def resize_favicon(src_path, dest_path, size=(32, 32)):
    with Image.open(src_path) as img:
        img = img.resize(size, Image.LANCZOS)
        img.save(dest_path, format='webp')

# Resize and copy favicon.ico to the docs directory
resize_favicon('content/favicon.ico', 'docs/favicon.ico')