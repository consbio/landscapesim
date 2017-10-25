var store = {};

store[1] = {
        name: "Castle Creek",
        description : "A sample ST-Sim library developed for a semi-arid shrub-steppe ecosystem in southwest Idaho (Castle Creek).",
        author: "Michael S. O'Donnell",
        date: "2015",
        //extent: [[42.371734722510496, -117.02842712402345], [42.89206418807337, -115.92979431152345]],
        extent: [[42.55790050289854, -116.60960551441471], [42.7996938297675, -116.27533823026967]],
        zoom: 12,
        // Actual Library Name: Alias
        management_actions_filter: {
            "Thin-Mech-Chem": "Thin-Mech-Chem",
            "SENN-Maintenance": "SENN-Maintenance",
            "Restoration Tree Encroached L": "Restoration Tree Encroached L",
            "Restoration Tree Encroached H": "Restoration Tree Encroached H",
            "Restoration Depleted Sage L": "Restoration Depleted Sage L",
            "Restoration Depleted Sage H": "Restoration Depleted Sage H",
            "Restoration Depleted Sage": "Restoration Depleted Sage",
            "Restoration Annual Grass L": "Restoration Annual Grass L",
            "Restoration Annual Grass H": "Restoration Annual Grass H",
            "Restoration Annual Grass": "Restoration Annual Grass",
            "Reference Restoration L": "Reference Restoration L",
            "Reference Restoration H": "Reference Restoration H",
            "CWG-Seed": "CWG-Seed",
            "CWG-Restoration": "CWG-Restoration",
            "Replacement Fire": "Prescribed Fire"
        }
};

var downloadCsvURL = '/api/download-csv/';
var downloadPdfURL = '/api/download-pdf/';
var requestSpatialDataURL = '/api/request-spatial-data/';

// Available ST-Sim reports to be downloaded.
var availableReports = {
       
    // PDF report
    'overview': {
        'label': 'Overview',
        'ext': '.pdf',
        'url': downloadPdfURL
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
    },
}
