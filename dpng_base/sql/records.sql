ALTER TABLE public.res_users
    ADD COLUMN sia_id character varying COLLATE pg_catalog."default";

COMMENT ON COLUMN public.res_users.sia_id
    IS 'SIA ID';



ALTER TABLE public.res_partner
    ADD COLUMN guardaparque boolean;

COMMENT ON COLUMN public.res_partner.guardaparque
    IS 'Es Guardaparque';



ALTER TABLE public.res_partner
    ADD COLUMN id_theos character varying COLLATE pg_catalog."default";

COMMENT ON COLUMN public.res_partner.id_theos
    IS 'Theos ID';
