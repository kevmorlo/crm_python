-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : sam. 04 mars 2023 à 21:27
-- Version du serveur : 8.0.31
-- Version de PHP : 8.0.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `crm`
--

-- --------------------------------------------------------

--
-- Structure de la table `contact`
--

DROP TABLE IF EXISTS `contact`;
CREATE TABLE IF NOT EXISTS `contact` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(45) NOT NULL,
  `email` varchar(255) NOT NULL,
  `telephone` varchar(30) DEFAULT NULL,
  `entreprise_siret` varchar(45) NOT NULL,
  `poste_idposte` int DEFAULT NULL,
  `statut_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_contact_entreprise_idx` (`entreprise_siret`),
  KEY `fk_contact_poste1_idx` (`poste_idposte`),
  KEY `fk_contact_statut1_idx` (`statut_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure de la table `description`
--

DROP TABLE IF EXISTS `description`;
CREATE TABLE IF NOT EXISTS `description` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date_de_creation` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `description` varchar(255) NOT NULL,
  `contact_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_description_contact1_idx` (`contact_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure de la table `entreprise`
--

DROP TABLE IF EXISTS `entreprise`;
CREATE TABLE IF NOT EXISTS `entreprise` (
  `siret` varchar(30) NOT NULL,
  `nom` varchar(45) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `adresse` varchar(100) NOT NULL,
  `ville` varchar(45) NOT NULL,
  `code_postal` varchar(45) NOT NULL,
  `url` varchar(1000) DEFAULT NULL,
  `utilisateur_id` int NOT NULL,
  PRIMARY KEY (`siret`,`utilisateur_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure de la table `facturation`
--

DROP TABLE IF EXISTS `facturation`;
CREATE TABLE IF NOT EXISTS `facturation` (
  `contact_id` int NOT NULL,
  `facture_num_facture` int NOT NULL,
  PRIMARY KEY (`contact_id`,`facture_num_facture`),
  KEY `fk_contact_has_facture_facture1_idx` (`facture_num_facture`),
  KEY `fk_contact_has_facture_contact1_idx` (`contact_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure de la table `facture`
--

DROP TABLE IF EXISTS `facture`;
CREATE TABLE IF NOT EXISTS `facture` (
  `num_facture` int NOT NULL AUTO_INCREMENT,
  `date` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `utilisateur_siren` varchar(20) NOT NULL,
  PRIMARY KEY (`num_facture`),
  KEY `fk_facture_utilisateur1_idx` (`utilisateur_siren`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure de la table `poste`
--

DROP TABLE IF EXISTS `poste`;
CREATE TABLE IF NOT EXISTS `poste` (
  `id` int NOT NULL,
  `nom` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idposte_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure de la table `referencement`
--

DROP TABLE IF EXISTS `referencement`;
CREATE TABLE IF NOT EXISTS `referencement` (
  `entreprise_siret` varchar(30) NOT NULL,
  `entreprise_utilisateur_id` int NOT NULL,
  `utilisateur_siren` varchar(20) NOT NULL,
  PRIMARY KEY (`entreprise_siret`,`entreprise_utilisateur_id`,`utilisateur_siren`),
  KEY `fk_entreprise_has_utilisateur_utilisateur1_idx` (`utilisateur_siren`),
  KEY `fk_entreprise_has_utilisateur_entreprise1_idx` (`entreprise_siret`,`entreprise_utilisateur_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure de la table `statut`
--

DROP TABLE IF EXISTS `statut`;
CREATE TABLE IF NOT EXISTS `statut` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure de la table `utilisateur`
--

DROP TABLE IF EXISTS `utilisateur`;
CREATE TABLE IF NOT EXISTS `utilisateur` (
  `siren` varchar(20) NOT NULL,
  `nom_entreprise` varchar(100) NOT NULL,
  `telephone` varchar(30) NOT NULL,
  `email` varchar(100) NOT NULL,
  `iban` varchar(27) NOT NULL,
  `adresse` varchar(100) NOT NULL,
  `ville` varchar(45) NOT NULL,
  `code_postal` varchar(45) NOT NULL,
  `mot_de_passe` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `sel` varchar(255) NOT NULL,
  PRIMARY KEY (`siren`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `contact`
--
ALTER TABLE `contact`
  ADD CONSTRAINT `fk_contact_entreprise` FOREIGN KEY (`entreprise_siret`) REFERENCES `entreprise` (`siret`),
  ADD CONSTRAINT `fk_contact_poste1` FOREIGN KEY (`poste_idposte`) REFERENCES `poste` (`id`),
  ADD CONSTRAINT `fk_contact_statut1` FOREIGN KEY (`statut_id`) REFERENCES `statut` (`id`);

--
-- Contraintes pour la table `description`
--
ALTER TABLE `description`
  ADD CONSTRAINT `fk_description_contact1` FOREIGN KEY (`contact_id`) REFERENCES `contact` (`id`);

--
-- Contraintes pour la table `facturation`
--
ALTER TABLE `facturation`
  ADD CONSTRAINT `fk_contact_has_facture_contact1` FOREIGN KEY (`contact_id`) REFERENCES `contact` (`id`),
  ADD CONSTRAINT `fk_contact_has_facture_facture1` FOREIGN KEY (`facture_num_facture`) REFERENCES `facture` (`num_facture`);

--
-- Contraintes pour la table `facture`
--
ALTER TABLE `facture`
  ADD CONSTRAINT `fk_facture_utilisateur1` FOREIGN KEY (`utilisateur_siren`) REFERENCES `utilisateur` (`siren`);

--
-- Contraintes pour la table `referencement`
--
ALTER TABLE `referencement`
  ADD CONSTRAINT `fk_entreprise_has_utilisateur_entreprise1` FOREIGN KEY (`entreprise_siret`,`entreprise_utilisateur_id`) REFERENCES `entreprise` (`siret`, `utilisateur_id`),
  ADD CONSTRAINT `fk_entreprise_has_utilisateur_utilisateur1` FOREIGN KEY (`utilisateur_siren`) REFERENCES `utilisateur` (`siren`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
