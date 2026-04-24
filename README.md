# Kavalakat REST API — Complete Documentation v2.0

**Base URL:** `http://127.0.0.1:8000/api/`  
**Production:** `https://yourdomain.com/api/`  
**Content-Type:** `application/json`  
**Auth:** JWT Bearer Token

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [Response Format](#2-response-format)
3. [Pages API](#3-pages-api)
4. [About API](#4-about-api)
5. [Portfolio API](#5-portfolio-api)
6. [Blog API](#6-blog-api)
7. [Contact API](#7-contact-api)
8. [Enquiry API](#8-enquiry-api)
9. [AI Blog Generator](#9-ai-blog-generator)
10. [Query Parameters](#10-query-parameters)
11. [Error Codes](#11-error-codes)
12. [Frontend Integration (React/Next.js)](#12-frontend-integration)

---

## 1. Authentication

### Obtain Token

```
POST /api/auth/token/
```

**Body:**
```json
{
  "username": "admin",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "access":  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Refresh Token

```
POST /api/auth/token/refresh/
Body: { "refresh": "<refresh_token>" }
```

### Verify Token

```
POST /api/auth/token/verify/
Body: { "token": "<access_token>" }
```

### Use Token in Requests

```
Authorization: Bearer <access_token>
```

> **Public endpoints** (GET) work without a token.  
> **Write operations** (POST/PUT/PATCH/DELETE) require `Authorization: Bearer <token>` header.

---

## 2. Response Format

### Success — Single Object
```json
{
  "success": true,
  "data": { "id": 1, "title": "..." }
}
```

### Success — List
```json
{
  "success": true,
  "count": 42,
  "data": [ {...}, {...} ]
}
```

### Success — Paginated
```json
{
  "success": true,
  "pagination": {
    "total":        42,
    "pages":        5,
    "current_page": 1,
    "page_size":    10,
    "next":         "http://127.0.0.1:8000/api/blog/?page=2",
    "previous":     null
  },
  "data": [ {...}, {...} ]
}
```

### Error
```json
{
  "success":     false,
  "status_code": 400,
  "message":     "title: This field is required.",
  "errors":      { "title": ["This field is required."] }
}
```

---

## 3. Pages API

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/pages/` | Public | List all active pages |
| GET | `/api/pages/{slug}/` | Public | Single page detail |
| POST | `/api/pages/` | Admin | Create page |
| PUT | `/api/pages/{slug}/` | Admin | Full update |
| PATCH | `/api/pages/{slug}/` | Admin | Partial update |
| DELETE | `/api/pages/{slug}/` | Admin | Delete page |
| POST | `/api/pages/{slug}/toggle-active/` | Admin | Toggle visibility |

### GET /api/pages/

```json
{
  "success": true,
  "count": 6,
  "data": [
    {
      "id": 1,
      "title": "Home",
      "slug": "home",
      "content": "<p>Welcome to Kavalakat</p>",
      "banner_image": null,
      "banner_image_url": null,
      "meta_title": "Kavalakat - Cement Trading",
      "meta_description": "Leading cement distributor in Kerala",
      "is_active": true,
      "order": 1,
      "created_at": "2026-01-15T09:30:00+05:30",
      "updated_at": "2026-01-15T09:30:00+05:30"
    }
  ]
}
```

### POST /api/pages/ (Admin)

```json
{
  "title": "About Us",
  "content": "<h2>About Kavalakat</h2><p>...</p>",
  "meta_title": "About Kavalakat",
  "meta_description": "Learn about Kavalakat company",
  "is_active": true,
  "order": 2
}
```

### Filters

```
GET /api/pages/?is_active=true
GET /api/pages/?search=home
GET /api/pages/?ordering=order
```

---

## 4. About API

### About Info (Singleton)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/about/` | Public | Company info |
| POST | `/api/about/` | Admin | Create |
| PUT | `/api/about/{id}/` | Admin | Update |
| PATCH | `/api/about/{id}/` | Admin | Partial update |

```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Kavalakat Group",
    "description": "Kerala's leading cement trading company...",
    "vision": "To be the most trusted building materials partner...",
    "mission": "Delivering quality cement and construction materials...",
    "founded_year": 1998,
    "employee_count": 120,
    "updated_at": "2026-01-15T09:30:00+05:30"
  }
}
```

### Strengths

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/strengths/` | Public | List active strengths |
| POST | `/api/strengths/` | Admin | Create |
| PUT | `/api/strengths/{id}/` | Admin | Update |
| PATCH | `/api/strengths/{id}/` | Admin | Partial |
| DELETE | `/api/strengths/{id}/` | Admin | Delete |
| POST | `/api/strengths/{id}/toggle-active/` | Admin | Toggle |

**POST body:**
```json
{
  "title": "Quality Products",
  "description": "We only supply certified, ISI-marked products.",
  "icon": "fa-certificate",
  "order": 1,
  "is_active": true
}
```

### Milestones

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/milestones/` | Public | All milestones |
| POST | `/api/milestones/` | Admin | Create |
| PUT | `/api/milestones/{id}/` | Admin | Update |
| DELETE | `/api/milestones/{id}/` | Admin | Delete |

**POST body:**
```json
{
  "year": 2010,
  "title": "Expanded to 5 districts",
  "description": "Opened distribution centres in Thrissur, Palakkad...",
  "order": 3
}
```

### Projects

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/projects/` | Public |
| GET | `/api/projects/?is_featured=true` | Public |
| GET | `/api/projects/?search=cement` | Public |
| POST | `/api/projects/` | Admin |
| PUT | `/api/projects/{id}/` | Admin |
| DELETE | `/api/projects/{id}/` | Admin |
| POST | `/api/projects/{id}/toggle-featured/` | Admin |

### Gallery

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/gallery/` | Public |
| POST | `/api/gallery/` | Admin (multipart) |
| DELETE | `/api/gallery/{id}/` | Admin |
| POST | `/api/gallery/{id}/toggle-active/` | Admin |

**Image Upload (multipart/form-data):**
```
POST /api/gallery/
Content-Type: multipart/form-data
Authorization: Bearer <token>

image=<file>
title=Warehouse Interior
order=1
is_active=true
```

---

## 5. Portfolio API

### Portfolio Page — Single Call (Frontend Recommended)

```
GET /api/portfolio/page/
```

Returns the complete 3-column layout in one API call — perfect for React/Next.js:

```json
{
  "success": true,
  "data": {
    "trading": [
      { "id": 1, "name": "CEMENT", "description": "", "image_url": null,
        "tags": "cement, OPC, PPC", "category_name": "Trading",
        "is_featured": false, "is_active": true, "order": 1 },
      { "id": 2, "name": "STEELS", ... },
      { "id": 3, "name": "ROOFING SOLUTIONS", ... },
      { "id": 4, "name": "WHITE CEMENT PAINT", ... },
      { "id": 5, "name": "CONSTRUCTION CHEMICALS", ... }
    ],
    "distribution": [
      { "id": 6, "name": "ULTRATECH", ... },
      { "id": 7, "name": "JK CEMENT", ... },
      { "id": 8, "name": "TATA STEEL", ... },
      { "id": 9, "name": "JSW STEEL", ... },
      { "id": 10, "name": "ASIAN PAINTS", ... }
    ],
    "services": [
      { "id": 11, "name": "KAVALAKAT GROUP", ... },
      { "id": 12, "name": "ALITE ENCLAVES", ... },
      { "id": 13, "name": "NEEY VEDHYAM", ... }
    ]
  }
}
```

### Categories

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/portfolio/categories/` | Public | List categories |
| GET | `/api/portfolio/categories/Trading/` | Public | Category + items |
| POST | `/api/portfolio/categories/` | Admin | Create |
| PUT | `/api/portfolio/categories/Trading/` | Admin | Update |
| DELETE | `/api/portfolio/categories/Trading/` | Admin | Delete |
| POST | `/api/portfolio/categories/Trading/toggle-active/` | Admin | Toggle |

### Items

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/portfolio/items/` | Public | All items |
| GET | `/api/portfolio/items/{id}/` | Public | Item detail |
| GET | `/api/portfolio/items/?category__name=Trading` | Public | Filter |
| GET | `/api/portfolio/items/?is_featured=true` | Public | Featured |
| GET | `/api/portfolio/items/?search=cement` | Public | Search |
| POST | `/api/portfolio/items/` | Admin | Create |
| PUT | `/api/portfolio/items/{id}/` | Admin | Update |
| PATCH | `/api/portfolio/items/{id}/` | Admin | Partial |
| DELETE | `/api/portfolio/items/{id}/` | Admin | Delete |
| POST | `/api/portfolio/items/{id}/toggle-featured/` | Admin | Toggle |
| POST | `/api/portfolio/items/{id}/toggle-active/` | Admin | Toggle |

**POST /api/portfolio/items/ body:**
```json
{
  "name": "cement",
  "description": "OPC and PPC cement in all grades",
  "category": 1,
  "tags": "cement, OPC, PPC, construction",
  "is_featured": false,
  "is_active": true,
  "order": 1
}
```
> Note: `name` is auto-uppercased to `"CEMENT"` on save.

---

## 6. Blog API

### Categories

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/blog/categories/` | Public |
| GET | `/api/blog/categories/{slug}/` | Public |
| POST | `/api/blog/categories/` | Admin |
| PUT | `/api/blog/categories/{slug}/` | Admin |
| DELETE | `/api/blog/categories/{slug}/` | Admin |

**Response:**
```json
{
  "id": 1,
  "name": "Cement Grade",
  "slug": "cement-grade",
  "description": "Posts about cement grades and types",
  "order": 1,
  "post_count": 5
}
```

### Posts

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/blog/` | Public | Published posts |
| GET | `/api/blog/{slug}/` | Public | Post detail (views++) |
| GET | `/api/blog/featured/` | Public | Featured posts |
| GET | `/api/blog/category/{name}/` | Public | Posts by category |
| GET | `/api/blog/?search=cement` | Public | Full-text search |
| GET | `/api/blog/?category__slug=cement-grade` | Public | Filter by category |
| GET | `/api/blog/?status=draft` | Admin | Filter by status |
| POST | `/api/blog/` | Admin | Create post |
| PUT | `/api/blog/{slug}/` | Admin | Full update |
| PATCH | `/api/blog/{slug}/` | Admin | Partial update |
| DELETE | `/api/blog/{slug}/` | Admin | Delete |
| POST | `/api/blog/{slug}/publish/` | Admin | Publish draft |
| POST | `/api/blog/{slug}/unpublish/` | Admin | Move to draft |
| POST | `/api/blog/{slug}/toggle-featured/` | Admin | Toggle featured |

**POST /api/blog/ body:**
```json
{
  "title": "Types of Cement Used in Kerala Construction",
  "content": "## Introduction\n\nCement is one of the most important...",
  "excerpt": "A complete guide to cement types used in Kerala",
  "category": 1,
  "status": "published",
  "tags": "cement, OPC, PPC, Kerala, construction",
  "is_featured": false,
  "meta_title": "Cement Types in Kerala — Kavalakat",
  "meta_description": "Learn about OPC, PPC and other cement types",
  "published_at": "2026-01-15T09:00:00+05:30"
}
```

**Post List Response:**
```json
{
  "id": 1,
  "title": "Types of Cement Used in Kerala Construction",
  "slug": "types-of-cement-used-in-kerala-construction",
  "excerpt": "A complete guide...",
  "image": null,
  "image_url": null,
  "category": 1,
  "category_name": "Cement Grade",
  "category_slug": "cement-grade",
  "author": 1,
  "author_name": "Admin User",
  "status": "published",
  "tags": "cement, OPC, PPC",
  "is_featured": false,
  "is_ai_generated": false,
  "views": 142,
  "created_at": "2026-01-15T09:30:00+05:30",
  "published_at": "2026-01-15T09:00:00+05:30"
}
```

---

## 7. Contact API

### Contact Info (Singleton)

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/contact/` | Public |
| POST | `/api/contact/` | Admin |
| PUT | `/api/contact/{id}/` | Admin |
| PATCH | `/api/contact/{id}/` | Admin |

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "phone": "+91 98765 43210",
    "alt_phone": "+91 98765 43211",
    "email": "info@kavalakat.com",
    "alt_email": "sales@kavalakat.com",
    "address": "Kavalakat Building, NH-66, Calicut",
    "city": "Kozhikode",
    "state": "Kerala",
    "pincode": "673001",
    "map_embed_url": "https://www.google.com/maps/embed?...",
    "whatsapp": "+91 98765 43210",
    "facebook": "https://facebook.com/kavalakat",
    "instagram": "https://instagram.com/kavalakat",
    "linkedin": "https://linkedin.com/company/kavalakat",
    "youtube": "https://youtube.com/@kavalakat",
    "business_hours": "Mon-Sat: 9AM – 6PM",
    "updated_at": "2026-01-15T09:30:00+05:30"
  }
}
```

### Careers

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/careers/` | Public | Active job listings |
| GET | `/api/careers/{id}/` | Public | Job detail |
| GET | `/api/careers/?job_type=Full-Time` | Public | Filter |
| POST | `/api/careers/` | Admin | Create job |
| PUT | `/api/careers/{id}/` | Admin | Update |
| DELETE | `/api/careers/{id}/` | Admin | Delete |
| POST | `/api/careers/{id}/toggle-active/` | Admin | Open/close |

---

## 8. Enquiry API

### Submit Enquiry (Public — No Token Required)

```
POST /api/enquiry/
```

**Body:**
```json
{
  "name": "Rajan Kumar",
  "email": "rajan@example.com",
  "phone": "+91 9876543210",
  "company": "Kumar Constructions",
  "subject": "Bulk cement quote for housing project",
  "message": "We need pricing for 500 bags of OPC 53 Grade cement for our Kozhikode project.",
  "enquiry_type": "quote"
}
```

> `enquiry_type` options: `general` | `career` | `quote` | `support`

**Response:**
```json
{
  "success": true,
  "message": "Thank you! We will get back to you within 24 hours.",
  "data": {
    "id": 42,
    "name": "Rajan Kumar",
    "email": "rajan@example.com",
    "phone": "+91 9876543210",
    "company": "Kumar Constructions",
    "subject": "Bulk cement quote for housing project",
    "message": "We need pricing for 500 bags...",
    "enquiry_type": "quote",
    "created_at": "2026-04-22T14:30:00+05:30"
  }
}
```

### Admin Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/enquiry/` | Admin | List all |
| GET | `/api/enquiry/{id}/` | Admin | Detail (auto marks read) |
| PATCH | `/api/enquiry/{id}/` | Admin | Update status/note |
| DELETE | `/api/enquiry/{id}/` | Admin | Delete |
| POST | `/api/enquiry/{id}/mark-replied/` | Admin | Mark replied |
| POST | `/api/enquiry/{id}/mark-closed/` | Admin | Close |
| GET | `/api/enquiry/stats/` | Admin | Count by status |

**Stats Response:**
```json
{
  "success": true,
  "data": {
    "new":     5,
    "read":    12,
    "replied": 28,
    "closed":  7,
    "total":   52
  }
}
```

---

## 9. AI Blog Generator

```
POST /api/ai/generate-blog/
Authorization: Bearer <token>
```

**Body:**
```json
{
  "topic": "benefits of PPC cement in Kerala construction",
  "save_as_draft": true,
  "category_id": 1,
  "author_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "log_id": 7,
    "topic": "benefits of PPC cement in Kerala construction",
    "title": "Why PPC Cement is the Best Choice for Kerala Builders",
    "excerpt": "Discover why Portland Pozzolana Cement is ideal for Kerala's climate...",
    "content": "## Introduction\n\nKerala's humid climate...",
    "tags": "PPC cement, Kerala construction, building materials",
    "meta_title": "PPC Cement Benefits — Kavalakat",
    "meta_description": "Learn why PPC cement suits Kerala's climate and construction needs",
    "model_used": "gpt-4o-mini",
    "tokens_used": 924,
    "saved_as_post": true,
    "post_id": 14,
    "post_slug": "why-ppc-cement-is-the-best-choice-for-kerala-builders"
  }
}
```

### AI Logs (Admin)

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/ai/logs/` | Admin |
| GET | `/api/ai/logs/{id}/` | Admin |
| DELETE | `/api/ai/logs/{id}/` | Admin |

---

## 10. Query Parameters

All list endpoints support these parameters:

| Parameter | Example | Description |
|-----------|---------|-------------|
| `?page=` | `?page=2` | Page number |
| `?page_size=` | `?page_size=20` | Items per page (max 100) |
| `?search=` | `?search=cement` | Full-text search |
| `?ordering=` | `?ordering=-created_at` | Sort field (- for descending) |
| `?is_active=` | `?is_active=true` | Filter active |
| `?is_featured=` | `?is_featured=true` | Filter featured |
| `?status=` | `?status=published` | Filter by status (blog) |
| `?category__name=` | `?category__name=Trading` | Filter by category name |
| `?job_type=` | `?job_type=Full-Time` | Filter careers |

---

## 11. Error Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Validation error — check `errors` field |
| 401 | Unauthorized — missing or invalid token |
| 403 | Forbidden — not enough permissions |
| 404 | Not found |
| 500 | Server error |
| 502 | OpenAI API error (AI endpoint only) |

---

## 12. Frontend Integration

### JavaScript / React (Fetch)

```javascript
const API_BASE = "http://127.0.0.1:8000/api";

// ── Get auth token ────────────────────────────────────────────────────────────
async function getToken(username, password) {
  const res = await fetch(`${API_BASE}/auth/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  localStorage.setItem("access_token",  data.access);
  localStorage.setItem("refresh_token", data.refresh);
  return data;
}

// ── Auth headers ──────────────────────────────────────────────────────────────
function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
  };
}

// ── Portfolio page (3-column layout) ─────────────────────────────────────────
async function getPortfolio() {
  const res = await fetch(`${API_BASE}/portfolio/page/`);
  const { data } = await res.json();
  // data.trading      → array of Trading items
  // data.distribution → array of Distribution items
  // data.services     → array of Services items
  return data;
}

// ── Blog posts ────────────────────────────────────────────────────────────────
async function getBlogPosts({ page = 1, search = "", category = "" } = {}) {
  const params = new URLSearchParams({ page, ...(search && { search }), ...(category && { "category__slug": category }) });
  const res = await fetch(`${API_BASE}/blog/?${params}`);
  return res.json();
  // Returns: { success, pagination: { total, pages, current_page, next, previous }, data: [...] }
}

async function getBlogPost(slug) {
  const res = await fetch(`${API_BASE}/blog/${slug}/`);
  return res.json();
}

// ── Submit enquiry ────────────────────────────────────────────────────────────
async function submitEnquiry(formData) {
  const res = await fetch(`${API_BASE}/enquiry/`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(formData),
  });
  return res.json();
}

// ── Contact info ──────────────────────────────────────────────────────────────
async function getContact() {
  const res = await fetch(`${API_BASE}/contact/`);
  const { data } = await res.json();
  return data;
}

// ── Admin: Create blog post ───────────────────────────────────────────────────
async function createBlogPost(postData) {
  const res = await fetch(`${API_BASE}/blog/`, {
    method:  "POST",
    headers: authHeaders(),
    body:    JSON.stringify(postData),
  });
  return res.json();
}

// ── Admin: Generate AI blog ───────────────────────────────────────────────────
async function generateAIBlog(topic, saveAsDraft = false, categoryId = null) {
  const res = await fetch(`${API_BASE}/ai/generate-blog/`, {
    method:  "POST",
    headers: authHeaders(),
    body:    JSON.stringify({ topic, save_as_draft: saveAsDraft, category_id: categoryId }),
  });
  return res.json();
}

// ── Upload image (gallery/project) ───────────────────────────────────────────
async function uploadGalleryImage(file, title = "", order = 0) {
  const form = new FormData();
  form.append("image", file);
  form.append("title", title);
  form.append("order", order);
  form.append("is_active", "true");
  const res = await fetch(`${API_BASE}/gallery/`, {
    method:  "POST",
    headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` },
    body:    form,
  });
  return res.json();
}
```

### Next.js (Server-Side)

```javascript
// lib/api.js
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export async function getPortfolio() {
  const res = await fetch(`${API_BASE}/portfolio/page/`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch portfolio");
  const json = await res.json();
  return json.data;
}

export async function getBlogPosts(page = 1) {
  const res = await fetch(`${API_BASE}/blog/?page=${page}`, { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("Failed to fetch blog posts");
  return res.json();
}

export async function getBlogPost(slug) {
  const res = await fetch(`${API_BASE}/blog/${slug}/`, { next: { revalidate: 300 } });
  if (!res.ok) return null;
  const json = await res.json();
  return json.data;
}

export async function getAbout() {
  const res = await fetch(`${API_BASE}/about/`, { next: { revalidate: 3600 } });
  const json = await res.json();
  return json.data;
}

export async function getContact() {
  const res = await fetch(`${API_BASE}/contact/`, { next: { revalidate: 3600 } });
  const json = await res.json();
  return json.data;
}
```

### Environment Variables

```bash
# .env.local (Next.js)
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api

# Production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
```

---

## Complete Endpoin
