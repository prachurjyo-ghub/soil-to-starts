import { redirect } from "next/navigation";

/** Legacy temporary route; keep a redirect so old links still open the demo result page. */
export default function ResultMockRedirect() {
  redirect("/result-page");
}
