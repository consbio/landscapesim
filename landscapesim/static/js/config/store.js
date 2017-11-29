var store = {
    "Castle Creek": {
        name: "Castle Creek",
        description: "A sample ST-Sim library developed for a semi-arid shrub-steppe ecosystem in southwest Idaho (Castle Creek).",
        author: "Michael S. O'Donnell",
        date: "2015",
        extent: {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                [-116.60960551441471, 42.7996938297675],
                [-116.27533823026967, 42.7996938297675],
                [-116.27533823026967, 42.55790050289854],
                [-116.60960551441471, 42.55790050289854]
                ]]
            }
        },
        zoom: 11,
        enable3D: true,
        spatial: true,
        require_reporting_unit: false,
        default_region: '',
        management_actions_filter: {
            "Thin-Mech-Chem": "Thin-Mech-Chem",
            "SENN-Maintenance": "SENN-Maintenance",
            "Restoration Tree Encroached L": "Restoration Tree Encroached L",
            "Restoration Tree Encroached H": "Restoration Tree Encroached H",
            "Restoration Depleted Sage L": "Restoration Depleted Sage L",
            "Restoration Depleted Sage H": "Restoration Depleted Sage H",
            "Restoration Depleted Sage": "Restoration Depeleted Sage",
            "Restoration Annual Grass L": "Restoration Annual Grass L",
            "Restoration Annual Grass H": "Restoration Annual Grass H",
            "Restoration Annual Grass": "Restoration Annual Grass",
            "Reference Restoration L": "Reference Restoration L",
            "Reference Restoration H": "Referenc Restoration H",
            "CWG-Seed": "CWG-Seed",
            "CWG-Restoration": "CWG-Restoration",
            "Replacement Fire": "Prescribed Fire"
        },
        stratum_service: null,
        stateclass_service: null,
        timesteps: 'Years',
        max_timestep: 100,
        max_spatial_iteration: 5
    },
    "LANDFIRE": {
        name: "LANDFIRE",
        description: "Biophysical Settings Quantitative Models",
        author: "USGS",
        date: "2014",
        extent: null,
        zoom: 10,
        enable3D: false,
        spatial: false,
        require_reporting_unit: true,
        default_region: 'Watersheds',
        management_actions_filter: {},
        stratum_service: {
            url: 'http://landfire.cr.usgs.gov/arcgis/services/Landfire/US_130/MapServer/WMSServer?',
            layers: "US_130BPS",
            wms: true
        },
        stateclass_service: {
            url: 'http://landfire.cr.usgs.gov/arcgis/services/Landfire/US_130/MapServer/WMSServer?',
            layers: "US_130SCLASS",
            wms: true
        },
        timesteps: 'Years',
        max_timestep: null,
        max_spatial_iteration: null
    }
};

var downloadCsvURL = '/api/download-csv/';
var requestPDFDataURL = '/api/request-pdf/';
var requestSpatialDataURL = '/api/request-spatial-data/';

// Available ST-Sim reports to be downloaded.
var availableReports = {
       
    // PDF report
    'overview': {
        'label': 'Overview',
        'ext': '.pdf',
        'url': requestPDFDataURL
    },

    // Spatial data download
    'spatial-data': {
        'label': 'Spatial Data',
        'ext': '.zip',
        'url': requestSpatialDataURL
    },

    // CSV reports
    'stateclass-summary' : {
        'label': 'Stateclass',
        'ext': '.csv',
        'url': downloadCsvURL
    },
    'transition-summary' : {
        'label': 'Transitions',
        'ext': '.csv',
        'url': downloadCsvURL
    },
    'transition-stateclass-summary' : {
        'label': 'Transitions by Stateclass',
        'ext': '.csv',
        'url': downloadCsvURL
    }
};
