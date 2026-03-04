/* BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated. */
/* KR-071: Yetkisiz erişim durumunda kullanıcıya bilgi verilir. */

import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Yetkisiz Erişim",
};

export default function ForbiddenPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col items-center justify-center gap-4 px-4 text-center">
      <h1 className="text-3xl font-semibold text-slate-900">Yetkisiz Erişim</h1>
      <p className="text-slate-600">Bu sayfaya erişim yetkiniz bulunmamaktadır.</p>
      <Link href="/" className="rounded bg-slate-900 px-4 py-2 text-sm text-white">
        Ana Sayfaya Dön
      </Link>
    </main>
  );
}
