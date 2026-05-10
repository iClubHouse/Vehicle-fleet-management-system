CREATE DATABASE AutoTrustDB;
GO
USE AutoTrustDB;
GO

CREATE TABLE Alquiler (
    id_alquiler                  INT IDENTITY(1,1)   NOT NULL PRIMARY KEY,
    id_cliente                   VARCHAR(24)         NOT NULL,
    id_vehiculo                  VARCHAR(24)         NOT NULL,
    fecha_inicio                 DATE                NOT NULL,
    fecha_devolucion_planificada DATE                NOT NULL,
    cantidad_dias                INT                 NOT NULL,
    costo_diario                 DECIMAL(10,2)       NOT NULL,
    costo_base                   DECIMAL(10,2)       NOT NULL,
    impuesto                     DECIMAL(10,2)       NOT NULL,
    seguro_diario                DECIMAL(10,2)       NOT NULL,
    costo_seguro                 DECIMAL(10,2)       NOT NULL,
    total                        DECIMAL(10,2)       NOT NULL,
    estado                       VARCHAR(20)         NOT NULL,
    fecha_registro               DATETIME            NOT NULL DEFAULT GETDATE()
);
GO

CREATE TABLE Devolucion (
    id_devolucion         INT IDENTITY(1,1)   NOT NULL PRIMARY KEY,
    id_alquiler           INT                 NOT NULL,
    fecha_devolucion_real DATE                NOT NULL,
    dias_atraso           INT                 NOT NULL,
    monto_penalizacion    DECIMAL(10,2)       NOT NULL,
    tiene_danio           BIT                 NOT NULL,
    total_devolucion      DECIMAL(10,2)       NOT NULL,
    FOREIGN KEY (id_alquiler) REFERENCES Alquiler(id_alquiler)
);
GO

CREATE TABLE Danio (
    id_danio      INT IDENTITY(1,1)   NOT NULL PRIMARY KEY,
    id_devolucion INT                 NOT NULL,
    descripcion   NVARCHAR(500)       NOT NULL,
    costo_danio   DECIMAL(10,2)       NOT NULL,
    FOREIGN KEY (id_devolucion) REFERENCES Devolucion(id_devolucion)
);
GO
