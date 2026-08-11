-- ============================================================
--  UNO Compétitif — schéma Supabase (synchro temps réel)
--  À exécuter UNE FOIS dans Supabase → SQL Editor → Run.
-- ============================================================
--
--  Modèle : tout l'état de l'app (joueurs + manches) tient dans une
--  seule ligne JSON (id = 1). Simple et suffisant pour un groupe d'amis.
--  L'app sème automatiquement les 23 manches d'origine si la ligne est vide.
--
--  Sécurité : accès complet avec la clé « anon » (publique). C'est adapté à
--  une petite ligue privée — ne partagez pas l'URL du site publiquement.
--  On pourra ajouter un mot de passe partagé plus tard si besoin.

create table if not exists public.app_state (
  id         int primary key,
  data       jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.app_state enable row level security;

-- Politiques : lecture + écriture pour la clé anon.
drop policy if exists "uno_read"   on public.app_state;
drop policy if exists "uno_insert" on public.app_state;
drop policy if exists "uno_update" on public.app_state;
create policy "uno_read"   on public.app_state for select using (true);
create policy "uno_insert" on public.app_state for insert with check (true);
create policy "uno_update" on public.app_state for update using (true) with check (true);

-- Temps réel : diffuser les changements de cette table.
-- (Ignore l'erreur « already member » si vous relancez le script.)
do $$
begin
  alter publication supabase_realtime add table public.app_state;
exception when duplicate_object then null;
end $$;
