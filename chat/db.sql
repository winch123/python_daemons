-- phpMyAdmin SQL Dump
-- version 4.0.10.8
-- http://www.phpmyadmin.net
--
-- Хост: localhost
-- Время создания: Окт 27 2016 г., 10:49
-- Версия сервера: 5.5.42
-- Версия PHP: 5.4.45

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- База данных: `visit`
--

-- --------------------------------------------------------

--
-- Структура таблицы `chat_active_seances`
--

CREATE TABLE IF NOT EXISTS `chat_active_seances` (
  `user` int(10) unsigned NOT NULL,
  `partner` int(10) unsigned NOT NULL,
  `ord` int(10) unsigned DEFAULT NULL,
  UNIQUE KEY `user_2` (`user`,`partner`,`ord`),
  KEY `user` (`user`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Структура таблицы `chat_messages`
--

CREATE TABLE IF NOT EXISTS `chat_messages` (
  `t` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `from_u` int(10) unsigned NOT NULL,
  `to_u` int(10) unsigned NOT NULL,
  `ord` int(10) unsigned NOT NULL,
  `text` text COLLATE utf8_unicode_ci NOT NULL,
  `t_read` timestamp NULL DEFAULT NULL,
  `m_type` tinyint(3) unsigned NOT NULL,
  UNIQUE KEY `t` (`t`,`from_u`,`to_u`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;



---- BD  opsos

CREATE TABLE IF NOT EXISTS `chat_user_cache` (
  `uid` int(10) unsigned NOT NULL,
  `site` tinyint(3) unsigned NOT NULL,
  `st_cache` text CHARACTER SET utf8 NOT NULL,
  `t_cache` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `u_state` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `t_state` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  KEY `uid` (`uid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
