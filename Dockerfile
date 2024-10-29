FROM node:20.18.0-bullseye AS frontend-builder

COPY ./frontend /frontend
WORKDIR /frontend
RUN npm cache clean --force && npm install --legacy-peer-deps && npm run build && rm -rf node_modules

FROM python:3.11.10-slim-bullseye AS runtime

USER root

WORKDIR /home/pi/cellphone_modem_manager/app
COPY ./backend ./
RUN pip3 install . && rm -rf dist build cellphone_modem_manager.egg-info

COPY --from=frontend-builder /frontend/dist /home/pi/cellphone_modem_manager/app/api/static

EXPOSE 20038/tcp

# For manifest generation
LABEL version="0.1.0"
LABEL permissions='{ "ExposedPorts": { "20038/tcp": {} }, "HostConfig": { "Privileged": true, "Binds":["/root/.config:/root/.config", "/dev:/dev:rw"], "PortBindings": { "20038/tcp": [ { "HostPort": "" } ] } } }'
LABEL authors='[{ "name": "João Mário Lago", "email": "joaolago@bluerobotics.com" }, { "name": "Willian Galvani", "email": "willian@bluerobotics.com" }, { "name": "Patrick J. Pereira", "email": "patrickelectric@gmail.com" }]'
LABEL company='{ "about": "", "name": "Blue Robotics", "email": "support@bluerobotics.com" }'
LABEL type="device-integration"
LABEL readme='https://raw.githubusercontent.com/bluerobotics/cellphone-modem-manager/{tag}/README.md'
LABEL links='{ "website": "https://raw.githubusercontent.com/bluerobotics/cellphone-modem-manager/", "support": "https://raw.githubusercontent.com/bluerobotics/cellphone-modem-manager/" }'
LABEL requirements="core >= 1.3"

ENTRYPOINT ["python3", "main.py"]
