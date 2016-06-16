 curl -sL "http://developer.trimet.org/ws/V1/trips/tripplanner?fromPlace=pdx&toPlace=zoo&appID=1E642E0795074C45E19A57B41" \
    | xmllint --format - > '/c/dev_projects/ott/api/log/old_trimet_api_response.log'
