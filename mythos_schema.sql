--
-- PostgreSQL database dump
--

\restrict DIqeocHFI1cu3LqZ9OzrmkFQigKlA566gc5ctXola3oQEBv60piOWoVJfNEJhf8

-- Dumped from database version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: log_transaction_change(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.log_transaction_change() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Only log if this is an UPDATE (not INSERT)
    IF TG_OP = 'UPDATE' THEN
        -- Log amount changes
        IF OLD.amount IS DISTINCT FROM NEW.amount THEN
            INSERT INTO transaction_history (transaction_id, field_name, old_value, new_value, changed_by)
            VALUES (NEW.id, 'amount', OLD.amount::TEXT, NEW.amount::TEXT, 'system');
        END IF;
        
        -- Log category changes
        IF OLD.primary_category IS DISTINCT FROM NEW.primary_category THEN
            INSERT INTO transaction_history (transaction_id, field_name, old_value, new_value, changed_by)
            VALUES (NEW.id, 'primary_category', OLD.primary_category, NEW.primary_category, 'user');
        END IF;
        
        -- Log pending status changes
        IF OLD.is_pending IS DISTINCT FROM NEW.is_pending THEN
            INSERT INTO transaction_history (transaction_id, field_name, old_value, new_value, changed_by)
            VALUES (NEW.id, 'is_pending', OLD.is_pending::TEXT, NEW.is_pending::TEXT, 'plaid_update');
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.log_transaction_change() OWNER TO postgres;

--
-- Name: update_true_available_balance(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_true_available_balance() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    affected_account_id INTEGER;
BEGIN
    -- Determine which account(s) to update
    IF TG_OP = 'DELETE' THEN
        affected_account_id := OLD.payment_account_id;
    ELSE
        affected_account_id := NEW.payment_account_id;
    END IF;
    
    -- Update the account's obligated amount and true available balance
    UPDATE accounts
    SET 
        obligated_amount = (
            SELECT COALESCE(SUM(amount), 0)
            FROM obligations
            WHERE payment_account_id = accounts.id
              AND NOT fulfilled
              AND obligation_date <= CURRENT_DATE + INTERVAL '30 days'
        ),
        true_available_balance = available_balance - COALESCE(obligated_amount, 0),
        updated_at = NOW()
    WHERE id = affected_account_id;
    
    -- If UPDATE and payment account changed, update old account too
    IF TG_OP = 'UPDATE' AND OLD.payment_account_id != NEW.payment_account_id THEN
        UPDATE accounts
        SET 
            obligated_amount = (
                SELECT COALESCE(SUM(amount), 0)
                FROM obligations
                WHERE payment_account_id = accounts.id
                  AND NOT fulfilled
                  AND obligation_date <= CURRENT_DATE + INTERVAL '30 days'
            ),
            true_available_balance = available_balance - COALESCE(obligated_amount, 0),
            updated_at = NOW()
        WHERE id = OLD.payment_account_id;
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_true_available_balance() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounts (
    id integer NOT NULL,
    institution_id integer NOT NULL,
    plaid_account_id text NOT NULL,
    name text NOT NULL,
    official_name text,
    account_type text NOT NULL,
    account_subtype text,
    mask text,
    current_balance numeric(12,2),
    available_balance numeric(12,2),
    limit_balance numeric(12,2),
    currency text DEFAULT 'USD'::text,
    obligated_amount numeric(12,2) DEFAULT 0.00,
    true_available_balance numeric(12,2),
    is_active boolean DEFAULT true,
    last_balance_update timestamp without time zone,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT valid_account_type CHECK ((account_type = ANY (ARRAY['depository'::text, 'credit'::text, 'loan'::text, 'investment'::text, 'other'::text])))
);


ALTER TABLE public.accounts OWNER TO postgres;

--
-- Name: TABLE accounts; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.accounts IS 'Bank accounts from all institutions';


--
-- Name: COLUMN accounts.true_available_balance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.accounts.true_available_balance IS 'Available balance minus unfulfilled obligations';


--
-- Name: accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.accounts_id_seq OWNER TO postgres;

--
-- Name: accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.accounts_id_seq OWNED BY public.accounts.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name text NOT NULL,
    parent_category_id integer,
    category_type text,
    icon text,
    color text,
    is_system boolean DEFAULT false,
    is_active boolean DEFAULT true,
    sort_order integer,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT valid_category_type CHECK ((category_type = ANY (ARRAY['income'::text, 'expense'::text, 'transfer'::text, NULL::text])))
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- Name: TABLE categories; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.categories IS 'Transaction categories for organization and analysis';


--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_messages (
    message_id integer NOT NULL,
    user_uuid uuid,
    telegram_user_id bigint,
    conversation_id character varying(100),
    role character varying(20),
    content text NOT NULL,
    mode character varying(50),
    model_used character varying(50),
    cypher_generated text,
    sql_generated text,
    response_time_ms integer,
    error_message text,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT chat_messages_role_check CHECK (((role)::text = ANY ((ARRAY['user'::character varying, 'assistant'::character varying])::text[])))
);


ALTER TABLE public.chat_messages OWNER TO postgres;

--
-- Name: chat_messages_message_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_messages_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_messages_message_id_seq OWNER TO postgres;

--
-- Name: chat_messages_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_messages_message_id_seq OWNED BY public.chat_messages.message_id;


--
-- Name: clothing_colors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clothing_colors (
    item_id uuid,
    color text
);


ALTER TABLE public.clothing_colors OWNER TO postgres;

--
-- Name: clothing_images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clothing_images (
    id integer NOT NULL,
    item_id uuid,
    filename text NOT NULL,
    original_filename text,
    view_type text
);


ALTER TABLE public.clothing_images OWNER TO postgres;

--
-- Name: clothing_images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clothing_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clothing_images_id_seq OWNER TO postgres;

--
-- Name: clothing_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clothing_images_id_seq OWNED BY public.clothing_images.id;


--
-- Name: clothing_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clothing_items (
    id uuid NOT NULL,
    brand text,
    garment_type text NOT NULL,
    gender_category text NOT NULL,
    size_label text,
    standardized_size text,
    condition text NOT NULL,
    country_of_manufacture text,
    original_retail_price numeric(10,2),
    estimated_resale_price numeric(10,2),
    care_instructions text,
    confidence_score numeric(3,2),
    inferred_fields text[],
    notes text,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.clothing_items OWNER TO postgres;

--
-- Name: clothing_materials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clothing_materials (
    item_id uuid,
    material text
);


ALTER TABLE public.clothing_materials OWNER TO postgres;

--
-- Name: institutions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.institutions (
    id integer NOT NULL,
    item_id text NOT NULL,
    access_token text NOT NULL,
    institution_id text NOT NULL,
    institution_name text NOT NULL,
    status text DEFAULT 'active'::text,
    last_successful_sync timestamp without time zone,
    last_sync_attempt timestamp without time zone,
    error_code text,
    error_message text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT valid_institution_status CHECK ((status = ANY (ARRAY['active'::text, 'requires_update'::text, 'error'::text, 'disabled'::text])))
);


ALTER TABLE public.institutions OWNER TO postgres;

--
-- Name: TABLE institutions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.institutions IS 'Plaid bank connections - one per institution';


--
-- Name: COLUMN institutions.item_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.institutions.item_id IS 'Plaid item_id - unique per connection';


--
-- Name: COLUMN institutions.access_token; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.institutions.access_token IS 'Plaid access token - keep secure';


--
-- Name: institutions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.institutions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.institutions_id_seq OWNER TO postgres;

--
-- Name: institutions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.institutions_id_seq OWNED BY public.institutions.id;


--
-- Name: obligations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.obligations (
    id integer NOT NULL,
    description text NOT NULL,
    amount numeric(12,2) NOT NULL,
    obligation_date date NOT NULL,
    source_account_id integer,
    payment_account_id integer,
    fulfilled boolean DEFAULT false,
    fulfilled_at timestamp without time zone,
    fulfilled_transaction_id bigint,
    notes text,
    created_by text DEFAULT 'user'::text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT future_obligation_or_fulfilled CHECK (((obligation_date >= CURRENT_DATE) OR (fulfilled = true)))
);


ALTER TABLE public.obligations OWNER TO postgres;

--
-- Name: TABLE obligations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.obligations IS 'Future payment commitments - critical for true available balance';


--
-- Name: obligations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.obligations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.obligations_id_seq OWNER TO postgres;

--
-- Name: obligations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.obligations_id_seq OWNED BY public.obligations.id;


--
-- Name: people; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.people (
    id integer NOT NULL,
    prefix character varying(20),
    first_name character varying(100) NOT NULL,
    middle_name character varying(100),
    last_name character varying(100) NOT NULL,
    suffix character varying(20),
    known_as character varying(100),
    display_text character varying(300),
    date_of_birth date,
    dob_year integer,
    dob_month integer,
    dob_day integer,
    time_of_birth time without time zone,
    birth_city character varying(100),
    birth_state character varying(100),
    birth_zip character varying(20),
    birth_country character varying(100),
    date_of_death date,
    dod_year integer,
    dod_month integer,
    dod_day integer,
    canonical_id character varying(200),
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(100),
    modified_by character varying(100)
);


ALTER TABLE public.people OWNER TO postgres;

--
-- Name: people_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.people_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.people_id_seq OWNER TO postgres;

--
-- Name: people_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.people_id_seq OWNED BY public.people.id;


--
-- Name: sync_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sync_log (
    id bigint NOT NULL,
    institution_id integer,
    sync_started_at timestamp without time zone NOT NULL,
    sync_completed_at timestamp without time zone,
    duration_ms integer,
    status text NOT NULL,
    transactions_added integer DEFAULT 0,
    transactions_updated integer DEFAULT 0,
    transactions_removed integer DEFAULT 0,
    balances_updated integer DEFAULT 0,
    error_code text,
    error_message text,
    sync_type text DEFAULT 'automatic'::text,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT valid_sync_status CHECK ((status = ANY (ARRAY['success'::text, 'partial'::text, 'failed'::text]))),
    CONSTRAINT valid_sync_type CHECK ((sync_type = ANY (ARRAY['automatic'::text, 'manual'::text, 'forced'::text])))
);


ALTER TABLE public.sync_log OWNER TO postgres;

--
-- Name: TABLE sync_log; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sync_log IS 'Log every sync attempt for monitoring and debugging';


--
-- Name: sync_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sync_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sync_log_id_seq OWNER TO postgres;

--
-- Name: sync_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sync_log_id_seq OWNED BY public.sync_log.id;


--
-- Name: transaction_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transaction_history (
    id bigint NOT NULL,
    transaction_id bigint NOT NULL,
    field_name text NOT NULL,
    old_value text,
    new_value text,
    changed_by text,
    changed_at timestamp without time zone DEFAULT now(),
    reason text
);


ALTER TABLE public.transaction_history OWNER TO postgres;

--
-- Name: TABLE transaction_history; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.transaction_history IS 'Track all changes to transactions for audit purposes';


--
-- Name: transaction_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transaction_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transaction_history_id_seq OWNER TO postgres;

--
-- Name: transaction_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transaction_history_id_seq OWNED BY public.transaction_history.id;


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transactions (
    id bigint NOT NULL,
    account_id integer NOT NULL,
    plaid_transaction_id text NOT NULL,
    transaction_date date NOT NULL,
    authorized_date date,
    post_date date,
    amount numeric(12,2) NOT NULL,
    currency text DEFAULT 'USD'::text,
    name text NOT NULL,
    merchant_name text,
    category text[],
    primary_category text,
    subcategory text,
    is_pending boolean DEFAULT false,
    transaction_type text,
    payment_channel text,
    location_address text,
    location_city text,
    location_region text,
    location_postal_code text,
    location_country text,
    notes text,
    tags text[],
    is_recurring boolean DEFAULT false,
    recurring_pattern_id integer,
    version integer DEFAULT 1,
    previous_version_id bigint,
    imported_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT positive_version CHECK ((version > 0))
);


ALTER TABLE public.transactions OWNER TO postgres;

--
-- Name: TABLE transactions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.transactions IS 'All transactions from all accounts';


--
-- Name: COLUMN transactions.amount; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.transactions.amount IS 'Plaid convention: positive = expense, negative = income';


--
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transactions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transactions_id_seq OWNER TO postgres;

--
-- Name: transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    username character varying(50) NOT NULL,
    telegram_id bigint,
    soul_canonical_id character varying(100),
    soul_display_name character varying(100),
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: accounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts ALTER COLUMN id SET DEFAULT nextval('public.accounts_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: chat_messages message_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages ALTER COLUMN message_id SET DEFAULT nextval('public.chat_messages_message_id_seq'::regclass);


--
-- Name: clothing_images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clothing_images ALTER COLUMN id SET DEFAULT nextval('public.clothing_images_id_seq'::regclass);


--
-- Name: institutions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutions ALTER COLUMN id SET DEFAULT nextval('public.institutions_id_seq'::regclass);


--
-- Name: obligations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.obligations ALTER COLUMN id SET DEFAULT nextval('public.obligations_id_seq'::regclass);


--
-- Name: people id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people ALTER COLUMN id SET DEFAULT nextval('public.people_id_seq'::regclass);


--
-- Name: sync_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sync_log ALTER COLUMN id SET DEFAULT nextval('public.sync_log_id_seq'::regclass);


--
-- Name: transaction_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transaction_history ALTER COLUMN id SET DEFAULT nextval('public.transaction_history_id_seq'::regclass);


--
-- Name: transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);


--
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);


--
-- Name: accounts accounts_plaid_account_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_plaid_account_id_key UNIQUE (plaid_account_id);


--
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (message_id);


--
-- Name: clothing_images clothing_images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clothing_images
    ADD CONSTRAINT clothing_images_pkey PRIMARY KEY (id);


--
-- Name: clothing_items clothing_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clothing_items
    ADD CONSTRAINT clothing_items_pkey PRIMARY KEY (id);


--
-- Name: institutions institutions_item_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutions
    ADD CONSTRAINT institutions_item_id_key UNIQUE (item_id);


--
-- Name: institutions institutions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutions
    ADD CONSTRAINT institutions_pkey PRIMARY KEY (id);


--
-- Name: obligations obligations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.obligations
    ADD CONSTRAINT obligations_pkey PRIMARY KEY (id);


--
-- Name: people people_canonical_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT people_canonical_id_key UNIQUE (canonical_id);


--
-- Name: people people_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT people_pkey PRIMARY KEY (id);


--
-- Name: sync_log sync_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sync_log
    ADD CONSTRAINT sync_log_pkey PRIMARY KEY (id);


--
-- Name: transaction_history transaction_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transaction_history
    ADD CONSTRAINT transaction_history_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_plaid_transaction_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_plaid_transaction_id_key UNIQUE (plaid_transaction_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_uuid);


--
-- Name: users users_telegram_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_telegram_id_key UNIQUE (telegram_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_accounts_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_accounts_active ON public.accounts USING btree (is_active);


--
-- Name: idx_accounts_institution; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_accounts_institution ON public.accounts USING btree (institution_id);


--
-- Name: idx_accounts_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_accounts_type ON public.accounts USING btree (account_type);


--
-- Name: idx_categories_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_categories_active ON public.categories USING btree (is_active);


--
-- Name: idx_categories_parent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_categories_parent ON public.categories USING btree (parent_category_id);


--
-- Name: idx_chat_messages_conversation; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_chat_messages_conversation ON public.chat_messages USING btree (conversation_id);


--
-- Name: idx_chat_messages_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_chat_messages_created ON public.chat_messages USING btree (created_at);


--
-- Name: idx_chat_messages_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_chat_messages_user ON public.chat_messages USING btree (user_uuid);


--
-- Name: idx_institutions_institution_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_institutions_institution_id ON public.institutions USING btree (institution_id);


--
-- Name: idx_institutions_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_institutions_status ON public.institutions USING btree (status);


--
-- Name: idx_obligations_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_obligations_date ON public.obligations USING btree (obligation_date) WHERE (NOT fulfilled);


--
-- Name: idx_obligations_payment_account; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_obligations_payment_account ON public.obligations USING btree (payment_account_id) WHERE (NOT fulfilled);


--
-- Name: idx_people_canonical_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_people_canonical_id ON public.people USING btree (canonical_id);


--
-- Name: idx_people_dob; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_people_dob ON public.people USING btree (date_of_birth);


--
-- Name: idx_people_last_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_people_last_name ON public.people USING btree (last_name);


--
-- Name: idx_sync_log_institution; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sync_log_institution ON public.sync_log USING btree (institution_id, sync_started_at DESC);


--
-- Name: idx_sync_log_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sync_log_status ON public.sync_log USING btree (status, sync_started_at DESC);


--
-- Name: idx_transaction_history_transaction; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transaction_history_transaction ON public.transaction_history USING btree (transaction_id, changed_at DESC);


--
-- Name: idx_transactions_account; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_account ON public.transactions USING btree (account_id, transaction_date DESC);


--
-- Name: idx_transactions_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_category ON public.transactions USING btree (primary_category);


--
-- Name: idx_transactions_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_date ON public.transactions USING btree (transaction_date DESC);


--
-- Name: idx_transactions_merchant; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_merchant ON public.transactions USING btree (merchant_name);


--
-- Name: idx_transactions_pending; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_pending ON public.transactions USING btree (is_pending) WHERE (is_pending = true);


--
-- Name: idx_transactions_plaid_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_plaid_id ON public.transactions USING btree (plaid_transaction_id);


--
-- Name: transactions trg_log_transaction_change; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_log_transaction_change AFTER UPDATE ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.log_transaction_change();


--
-- Name: obligations trg_update_available_balance; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_available_balance AFTER INSERT OR DELETE OR UPDATE ON public.obligations FOR EACH ROW EXECUTE FUNCTION public.update_true_available_balance();


--
-- Name: accounts accounts_institution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_institution_id_fkey FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: categories categories_parent_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_parent_category_id_fkey FOREIGN KEY (parent_category_id) REFERENCES public.categories(id);


--
-- Name: chat_messages chat_messages_user_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_user_uuid_fkey FOREIGN KEY (user_uuid) REFERENCES public.users(user_uuid);


--
-- Name: clothing_colors clothing_colors_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clothing_colors
    ADD CONSTRAINT clothing_colors_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.clothing_items(id);


--
-- Name: clothing_images clothing_images_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clothing_images
    ADD CONSTRAINT clothing_images_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.clothing_items(id);


--
-- Name: clothing_materials clothing_materials_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clothing_materials
    ADD CONSTRAINT clothing_materials_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.clothing_items(id);


--
-- Name: obligations obligations_fulfilled_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.obligations
    ADD CONSTRAINT obligations_fulfilled_transaction_id_fkey FOREIGN KEY (fulfilled_transaction_id) REFERENCES public.transactions(id);


--
-- Name: obligations obligations_payment_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.obligations
    ADD CONSTRAINT obligations_payment_account_id_fkey FOREIGN KEY (payment_account_id) REFERENCES public.accounts(id);


--
-- Name: obligations obligations_source_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.obligations
    ADD CONSTRAINT obligations_source_account_id_fkey FOREIGN KEY (source_account_id) REFERENCES public.accounts(id);


--
-- Name: sync_log sync_log_institution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sync_log
    ADD CONSTRAINT sync_log_institution_id_fkey FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE SET NULL;


--
-- Name: transaction_history transaction_history_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transaction_history
    ADD CONSTRAINT transaction_history_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.transactions(id) ON DELETE CASCADE;


--
-- Name: transactions transactions_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id) ON DELETE CASCADE;


--
-- Name: transactions transactions_previous_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_previous_version_id_fkey FOREIGN KEY (previous_version_id) REFERENCES public.transactions(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT CREATE ON SCHEMA public TO adge;


--
-- Name: FUNCTION log_transaction_change(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.log_transaction_change() TO adge;


--
-- Name: FUNCTION update_true_available_balance(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.update_true_available_balance() TO adge;


--
-- Name: TABLE accounts; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.accounts TO adge;


--
-- Name: SEQUENCE accounts_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.accounts_id_seq TO adge;


--
-- Name: TABLE categories; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.categories TO adge;


--
-- Name: SEQUENCE categories_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.categories_id_seq TO adge;


--
-- Name: TABLE chat_messages; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.chat_messages TO adge;


--
-- Name: SEQUENCE chat_messages_message_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.chat_messages_message_id_seq TO adge;


--
-- Name: TABLE clothing_colors; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.clothing_colors TO adge;


--
-- Name: TABLE clothing_images; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.clothing_images TO adge;


--
-- Name: SEQUENCE clothing_images_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.clothing_images_id_seq TO adge;


--
-- Name: TABLE clothing_items; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.clothing_items TO adge;


--
-- Name: TABLE clothing_materials; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.clothing_materials TO adge;


--
-- Name: TABLE institutions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.institutions TO adge;


--
-- Name: SEQUENCE institutions_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.institutions_id_seq TO adge;


--
-- Name: TABLE obligations; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.obligations TO adge;


--
-- Name: SEQUENCE obligations_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.obligations_id_seq TO adge;


--
-- Name: TABLE people; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.people TO adge;


--
-- Name: SEQUENCE people_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.people_id_seq TO adge;


--
-- Name: TABLE sync_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sync_log TO adge;


--
-- Name: SEQUENCE sync_log_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.sync_log_id_seq TO adge;


--
-- Name: TABLE transaction_history; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.transaction_history TO adge;


--
-- Name: SEQUENCE transaction_history_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.transaction_history_id_seq TO adge;


--
-- Name: TABLE transactions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.transactions TO adge;


--
-- Name: SEQUENCE transactions_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.transactions_id_seq TO adge;


--
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.users TO adge;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO adge;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO adge;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO adge;


--
-- PostgreSQL database dump complete
--

\unrestrict DIqeocHFI1cu3LqZ9OzrmkFQigKlA566gc5ctXola3oQEBv60piOWoVJfNEJhf8

