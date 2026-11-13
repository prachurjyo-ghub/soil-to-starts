import { get } from "@/server/local-api.mjs";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function GET(request) { return get(request, "health"); }
