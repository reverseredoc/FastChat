--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5
-- Dumped by pg_dump version 14.5

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: credentials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.credentials (
    username character varying(50) NOT NULL,
    password character varying(500) NOT NULL,
    pub_key bytea NOT NULL,
    pvt_key bytea NOT NULL
);


ALTER TABLE public.credentials OWNER TO postgres;

--
-- Name: groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.groups (
    name character varying(50) NOT NULL,
    admin character varying(50) NOT NULL,
    pub_key bytea NOT NULL,
    pvt_key1 bytea NOT NULL,
    pvt_key2 bytea,
    pvt_key3 bytea,
    pvt_key4 bytea,
    pvt_key5 bytea,
    pvt_key6 bytea,
    pvt_key7 bytea,
    pvt_key8 bytea,
    pvt_key9 bytea,
    pvt_key10 bytea,
    pvt_key11 bytea,
    pvt_key12 bytea,
    pvt_key13 bytea,
    pvt_key14 bytea,
    pvt_key15 bytea,
    pvt_key16 bytea,
    pvt_key17 bytea,
    pvt_key18 bytea,
    pvt_key19 bytea,
    pvt_key20 bytea,
    number integer NOT NULL,
    member1 character varying(50) NOT NULL,
    member2 character varying(50),
    member3 character varying(50),
    member4 character varying(50),
    member5 character varying(50),
    member6 character varying(50),
    member7 character varying(50),
    member8 character varying(50),
    member9 character varying(50),
    member10 character varying(50),
    member11 character varying(50),
    member12 character varying(50),
    member13 character varying(50),
    member14 character varying(50),
    member15 character varying(50),
    member16 character varying(50),
    member17 character varying(50),
    member18 character varying(50),
    member19 character varying(50),
    member20 character varying(50)
);


ALTER TABLE public.groups OWNER TO postgres;

--
-- Name: ind_msg; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ind_msg (
    sender character varying(50) NOT NULL,
    receiver character varying(50) NOT NULL,
    "time" timestamp without time zone NOT NULL,
    message bytea NOT NULL,
    grp character varying(50),
    extension character varying(20),
    size character varying(100),
    pvt_key bytea
);


ALTER TABLE public.ind_msg OWNER TO postgres;

--
-- Name: credentials credentials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credentials
    ADD CONSTRAINT credentials_pkey PRIMARY KEY (username);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (name);


--
-- PostgreSQL database dump complete
--

