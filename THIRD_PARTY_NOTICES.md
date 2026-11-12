# Third-party notices and release audit

The root Apache-2.0 license applies to original team-owned code/documentation. It does not relicense third-party dependencies, fonts, imagery, video, NASA marks or externally sourced data. Existing notices remain in place. Release clearance is pending until the rights checklist is reviewed.

| Item | Existing evidence | Required action |
| --- | --- | --- |
| Next.js, React, react-dom, react-icons, Tailwind, ESLint/config | Locked npm dependency tree; installed package notices | Retain upstream notices; inspect versions/licenses before release. |
| MapLibre GL JS 6.16.0 | npm dependency pinned in the existing lockfile; BSD-3-Clause, [deployed upstream license](prototype/public/reference/licenses/maplibre-gl.LICENSE.txt) | Retain the deployed upstream license beside the bundled library/worker (build optimization strips the worker header). Only the requested map dependency was added; framework versions remain unchanged. |
| geoBoundaries gbOpen BGD ADM2 (`BGD-ADM2-16705992`, revision `9469f09`) | [Snapshot/processing/aliases](data/admin/README.md); local source and output checksums; BBS / OCHA ROAP sources, declared [CC BY 3.0 IGO](https://creativecommons.org/licenses/by/3.0/igo/) | Credit geoBoundaries, BBS and OCHA ROAP, link license, and indicate property/minification changes. Geometry coordinates are preserved from upstream's simplified dataset. No endorsement/survey accuracy is claimed. |
| OpenFreeMap Liberty street/reference basemap | [Provider setup](https://openfreemap.org/quick_start/), default remote style; style source attributions retained | Keep OpenFreeMap / © OpenMapTiles / OpenStreetMap credits visible. No satellite claim, tile bulk download or offline tile cache is added. Custom styles must include their correct source attribution. |
| Supplied photos/video | [Asset credits](prototype/public/reference/assets/credits.txt) | Nadim/Prachurjo verify original URLs, rights and competition suitability. |
| Local font files and Google Fonts links | `prototype/public/assets/fonts/`, reference font copies and route links | Identify exact families/files and applicable licenses; retain required license texts. |
| Generated cursor | Existing credit identifies image-tool assistance | Preserve truthful AI disclosure and verify supplied reference rights. |
| NASA/local datasets | Source manifests required; integrated fixtures absent | Verify exact product rights and fixture redistribution before committing data. |

Fourteen identical asset files currently appear in both frontend asset locations (about 8.8 MB). These are preserved because supplied reference pages may depend on them. Consolidation requires path analysis and visual verification; duplicate bytes do not establish rights or unused status.

No NASA endorsement is claimed. Team members must submit only material they have rights to share and follow current official participant/media requirements. The board's rights gate remains open.
