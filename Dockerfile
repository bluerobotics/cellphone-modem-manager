FROM node:20.18.0-bullseye AS frontend-builder

COPY ./frontend /frontend
WORKDIR /frontend
RUN npm install && npm run build && rm -rf node_modules

FROM python:3.11.10-slim-bullseye AS runtime

WORKDIR /home/pi/lte_eg25_g/app
COPY ./backend ./
RUN pip3 install . && rm -rf dist build lte_eg25_g.egg-info

COPY --from=frontend-builder /frontend/dist /home/pi/lte_eg25_g/app/api/static

EXPOSE 9119/tcp

# For manifest generation
LABEL version="0.1.0"
LABEL permissions='{ "ExposedPorts": { "20038/tcp": {} }, "HostConfig": { "Binds":["/root/.config:/root/.config"], "PortBindings": { "20038/tcp": [ { "HostPort": "" } ] } } }'
LABEL authors='[{ "name": "João Mário Lago", "email": "joaolago@bluerobotics.com" }, { "name": "Willian Galvani", "email": "willian@bluerobotics.com" }, { "name": "Patrick J. Pereira", "email": "patrickelectric@gmail.com" }]'
LABEL company='{ "about": "", "name": "Blue Robotics", "email": "support@bluerobotics.com" }'
LABEL type="device-integration"
LABEL readme='https://raw.githubusercontent.com/bluerobotics/BlueOS-LTE-EG25-G/{tag}/README.md'
LABEL links='{ "website": "https://raw.githubusercontent.com/bluerobotics/BlueOS-LTE-EG25-G/", "support": "https://raw.githubusercontent.com/bluerobotics/BlueOS-LTE-EG25-G/" }'
LABEL requirements="core >= 1.3"

ENTRYPOINT ["python3", "main.py"]
