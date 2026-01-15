# Personal Blog

Personal Blog System built with Frappe Framework and Vue 3 + Frappe-UI.

## Features

- Article management with Markdown support
- Category and tag system
- Comment system with moderation
- Modern Vue 3 frontend with Frappe-UI
- Dark mode support
- Responsive design

## Installation

```bash
bench get-app personal_blog
bench --site your-site install-app personal_blog
```

## Development

### Backend

The backend is built with Frappe Framework, providing:
- DocTypes for Blog Post, Category, Tag, Comment
- RESTful APIs for frontend consumption
- Permission management

### Frontend

The frontend is built with Vue 3 and Frappe-UI:

```bash
cd apps/personal_blog/frontend
yarn install
yarn dev
```

## License

MIT
