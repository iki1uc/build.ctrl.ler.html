/* ============================================================
   OR.add.js – aktiviert (((OR))) für jede Datei im Ordner
   ============================================================ */

import { OR_KERNEL } from "./OR_KERNEL.js";

export function OR.add(file){
    const OR = OR_KERNEL(file);
    console.log(`(((OR))) aktiviert für: ${file}`, OR);
    return OR;
}
