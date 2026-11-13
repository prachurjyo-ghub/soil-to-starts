import { post } from "@/server/local-api.mjs";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function POST(request) { return post(request, "current_crop"); }
