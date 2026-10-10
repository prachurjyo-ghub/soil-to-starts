import Link from "next/link";
import { PiPlant } from "react-icons/pi";

export default function Brand({ workspace = false }) {
  return (
    <Link className="brand" href="/" aria-label="Soil to Stars home">
      <span className="brand-mark"><PiPlant /></span>
      <span className="brand-name">soil<span>to</span>stars<small>{workspace ? "FIELD INTELLIGENCE STUDIO" : "EARTH-LED FARM INTELLIGENCE"}</small></span>
    </Link>
  );
}
