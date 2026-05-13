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
    "meta_description": "Learn why PPC cement suits Kerala's climate",
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

## 12. Query Parameters

All list endpoints support:

| Parameter | Example | Description |
|-----------|---------|-------------|
| `?page=` | `?page=2` | Page number |
| `?page_size=` | `?page_size=20` | Items per page (max 100) |
| `?search=` | `?search=cement` | Full-text search |
| `?ordering=` | `?ordering=-created_at` | Sort (- for descending) |
| `?is_active=` | `?is_active=true` | Filter active |
| `?is_featured=` | `?is_featured=true` | Filter featured |
| `?status=` | `?status=published` | Blog status filter |
| `?year=` | `?year=2023` | Filter projects by year |
| `?category__name=` | `?category__name=Trading` | Portfolio filter |
| `?job_type=` | `?job_type=Full-Time` | Careers filter |
| `?department=` | `?department=Engineering` | Careers filter |
| `?enquiry_type=` | `?enquiry_type=quote` | Enquiry filter |

---

## 13. Error Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Validation error — check `errors` field |
| 401 | Unauthorized — missing or invalid token |
| 403 | Forbidden — insufficient permissions |
| 404 | Not found |
| 500 | Server error |
| 502 | OpenAI API error (AI endpoint only) |

---

## 14. Frontend Integration

### JavaScript / React (Fetch)

```javascript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

// ── Auth ──────────────────────────────────────────────────────────────────────
async function getToken(username, password) {
  const res = await fetch(`${API_BASE}/auth/token/`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ username, password }),
  });
  const data = await res.json();
  localStorage.setItem("access_token",  data.access);
  localStorage.setItem("refresh_token", data.refresh);
  return data;
}

function authHeaders() {
  return {
    "Content-Type":  "application/json",
    "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
  };
}

// ── About ─────────────────────────────────────────────────────────────────────
async function getAbout() {
  const res = await fetch(`${API_BASE}/about/`);
  const { data } = await res.json();
  return data;
}

async function getStrengths() {
  const res = await fetch(`${API_BASE}/strengths/`);
  const { data } = await res.json();
  return data;
}

async function getMilestones() {
  const res = await fetch(`${API_BASE}/milestones/`);
  const { data } = await res.json();
  return data;
  // Each milestone has: year, title, description, image_url, tags, tags_list
}

async function getProjects({ featured = false, search = "" } = {}) {
  const params = new URLSearchParams({
    ...(featured && { is_featured: "true" }),
    ...(search   && { search }),
  });
  const res = await fetch(`${API_BASE}/projects/?${params}`);
  const { data } = await res.json();
  return data;
  // Each project has: title, client, client_logo_url, client_location, tag, image_url, contact_url
}

async function getTeam() {
  const res = await fetch(`${API_BASE}/team/`);
  const { data } = await res.json();
  return data;
  // Each member has: name, role, image_url, social_platform, social_url
}

async function getGallery() {
  const res = await fetch(`${API_BASE}/gallery/`);
  const { data } = await res.json();
  return data;
}

// ── Office Locations ──────────────────────────────────────────────────────────
async function getLocations() {
  const res = await fetch(`${API_BASE}/locations/`);
  const { data } = await res.json();
  return data;
  // Returns array of: { city, address, map_url }
}

// ── Portfolio ─────────────────────────────────────────────────────────────────
async function getPortfolio() {
  const res = await fetch(`${API_BASE}/portfolio/page/`);
  const { data } = await res.json();
  return data;
  // data.trading / data.distribution / data.services
}

// ── Blog ──────────────────────────────────────────────────────────────────────
async function getBlogPosts({ page = 1, search = "", category = "" } = {}) {
  const params = new URLSearchParams({
    page,
    ...(search   && { search }),
    ...(category && { "category__slug": category }),
  });
  const res = await fetch(`${API_BASE}/blog/?${params}`);
  return res.json();
}

async function getBlogPost(slug) {
  const res = await fetch(`${API_BASE}/blog/${slug}/`);
  const { data } = await res.json();
  return data;
}

// ── Contact ───────────────────────────────────────────────────────────────────
async function getContact() {
  const res = await fetch(`${API_BASE}/contact/`);
  const { data } = await res.json();
  return data;
}

// ── Careers ───────────────────────────────────────────────────────────────────
async function getCareers({ jobType = "", search = "" } = {}) {
  const params = new URLSearchParams({
    ...(jobType && { job_type: jobType }),
    ...(search  && { search }),
  });
  const res = await fetch(`${API_BASE}/careers/?${params}`);
  const { data } = await res.json();
  return data;
  // Each career has: title, department, location, job_type, apply_url, deadline, is_expired
}

// ── Enquiry ───────────────────────────────────────────────────────────────────
async function submitEnquiry(formData) {
  const res = await fetch(`${API_BASE}/enquiry/`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(formData),
  });
  return res.json();
}

// ── Admin: Upload image ───────────────────────────────────────────────────────
async function uploadGalleryImage(file, title = "", order = 0) {
  const form = new FormData();
  form.append("image",     file);
  form.append("title",     title);
  form.append("order",     order);
  form.append("is_active", "true");
  const res = await fetch(`${API_BASE}/gallery/`, {
    method:  "POST",
    headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` },
    body:    form,
  });
  return res.json();
}

// ── Admin: Generate AI blog ───────────────────────────────────────────────────
async function generateAIBlog(topic, saveAsDraft = false, categoryId = null) {
  const res = await fetch(`${API_BASE}/ai/generate-blog/`, {
    method:  "POST",
    headers: authHeaders(),
    body:    JSON.stringify({
      topic,
      save_as_draft: saveAsDraft,
      category_id:   categoryId,
    }),
  });
  return res.json();
}
```

### Next.js (Server-Side)

```javascript
// lib/api.js
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export async function getAbout() {
  const res = await fetch(`${API_BASE}/about/`, { next: { revalidate: 3600 } });
  const json = await res.json();
  return json.data;
}

export async function getMilestones() {
  const res = await fetch(`${API_BASE}/milestones/`, { next: { revalidate: 3600 } });
  const json = await res.json();
  return json.data;
}

export async function getProjects(featured = false) {
  const url = featured
    ? `${API_BASE}/projects/?is_featured=true`
    : `${API_BASE}/projects/`;
  const res  = await fetch(url, { next: { revalidate: 1800 } });
  const json = await res.json();
  return json.data;
}

export async function getTeam() {
  const res  = await fetch(`${API_BASE}/team/`, { next: { revalidate: 3600 } });
  const json = await res.json();
  return json.data;
}

export async function getLocations() {
  const res  = await fetch(`${API_BASE}/locations/`, { next: { revalidate: 3600 } });
  const json = await res.json();
  return json.data;
}

export async function getCareers() {
  const res  = await fetch(`${API_BASE}/careers/`, { next: { revalidate: 300 } });
  const json = await res.json();
  return json.data;
}

export async function getPortfolio() {
  const res  = await fetch(`${API_BASE}/portfolio/page/`, { cache: "no-store" });
  const json = await res.json();
  return json.data;
}

export async function getBlogPosts(page = 1) {
  const res  = await fetch(`${API_BASE}/blog/?page=${page}`, { next: { revalidate: 60 } });
  return res.json();
}

export async function getBlogPost(slug) {
  const res = await fetch(`${API_BASE}/blog/${slug}/`, { next: { revalidate: 300 } });
  if (!res.ok) return null;
  const json = await res.json();
  return json.data;
}

export async function getContact() {
  const res  = await fetch(`${API_BASE}/contact/`, { next: { revalidate: 3600 } });
  const json = await res.json();
  return json.data;
}
```

### Environment Variables

```bash
# .env.local (Next.js / React)
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api

# Production
NEXT_PUBLIC_API_URL=https://kavalakat-api.onrender.com/api
```

---

## Complete Endpoint Summary

| Module | Endpoints |
|--------|-----------|
| Auth | `/api/auth/token/` · `/api/auth/token/refresh/` · `/api/auth/token/verify/` |
| Pages | `/api/pages/` |
| About | `/api/about/` |
| Strengths | `/api/strengths/` |
| Milestones | `/api/milestones/` |
| Projects | `/api/projects/` |
| Team | `/api/team/` |
| Gallery | `/api/gallery/` |
| Portfolio | `/api/portfolio/page/` · `/api/portfolio/categories/` · `/api/portfolio/items/` |
| Blog | `/api/blog/` · `/api/blog/categories/` |
| Contact | `/api/contact/` |
| Locations | `/api/locations/` |
| Careers | `/api/careers/` |
| Enquiry | `/api/enquiry/` |
| AI | `/api/ai/generate-blog/` · `/api/ai/logs/` |
| Docs | `/api/docs/` · `/api/docs/redoc/` · `/api/schema/` |