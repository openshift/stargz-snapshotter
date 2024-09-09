# Built from this template:
# https://github.com/openshift/release/blob/master/tools/hack/golang/package.spec
#
# See also: https://github.com/openshift/kubernetes/blob/master/openshift.spec

#debuginfo not supported with Go
%global debug_package %{nil}

# modifying the Go binaries breaks the DWARF debugging
%global __os_install_post %{_rpmconfigdir}/brp-compress

# %commit and %os_git_vars are intended to be set by tito custom builders provided
# in the .tito/lib directory. The values in this spec file will not be kept up to date.
%{!?commit: %global commit HEAD }
%global shortcommit %(c=%{commit}; echo ${c:0:7})
# os_git_vars needed to run hack scripts during rpm builds
%{!?os_git_vars: %global os_git_vars OS_GIT_VERSION='' OS_GIT_COMMIT='' OS_GIT_MAJOR='' OS_GIT_MINOR='' OS_GIT_TREE_STATE='' }
#%{!?os_git_vars: %global os_git_vars OS_GIT_VERSION='4.18.0-202409020842.p0.g28e4ebc.assembly.test-28e4ebc' OS_GIT_COMMIT='28e4ebc2271d444a86f5d10a0ab967b2c05aa313' OS_GIT_MAJOR='4' OS_GIT_MINOR='18' OS_GIT_PATCH=0 OS_GIT_TREE_STATE='' }

%if 0%{?skip_build}
%global do_build 0
%else
%global do_build 1
%endif
%if 0%{?skip_prep}
%global do_prep 0
%else
%global do_prep 1
%endif

%if 0%{?fedora} || 0%{?epel}
%global need_redistributable_set 0
%else
# Due to library availability, redistributable builds only work on x86_64
%ifarch x86_64
%global need_redistributable_set 1
%else
%global need_redistributable_set 0
%endif
%endif
%{!?make_redistributable: %global make_redistributable %{need_redistributable_set}}

#
# Customize from here.
#

%global golang_version 1.22.0
%{!?version: %global version 0.0.1}
%{!?release: %global release 1}
%global package_name stargz-snapshotter
%global product_name stargz-snapshotter
%global import_path github.com/containerd/stargz-snapshotter

Name:           %{package_name}
Version:        %{version}
Release:        %{release}%{?dist}
Summary:        Stargz Snapshotter is an implementation of snapshotter which acts as a plugin for container runtimes and enables to lazily pull container images leveraging stargz image format by Google.
License:        ASL 2.0
URL:            https://%{import_path}

Source0:        https://%{import_path}/archive/%{commit}/%{name}-%{version}.tar.gz
BuildRequires:  golang >= %{golang_version}

# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:  x86_64 aarch64 ppc64le s390x
%endif

### AUTO-BUNDLED-GEN-ENTRY-POINT

%description
Pulling image is one of the time-consuming steps in the container lifecycle.
Stargz Snapshotter is an implementation of snapshotter which aims to solve this problem
by lazy pulling. Lazy pulling here means a container can run without waiting
for the pull completion of the image and necessary chunks of the image are fetched on-demand.
https://github.com/containerd/stargz-snapshotter

%prep
%if 0%{do_prep}
%setup -q
%endif

%build
%if 0%{do_build}
%if 0%{make_redistributable}
# Create Binaries for all internally defined arches
%{os_git_vars} make build
%else
# Create Binaries only for building arch
%ifarch x86_64
  BUILD_PLATFORM="linux/amd64"
%endif
%ifarch %{ix86}
  BUILD_PLATFORM="linux/386"
%endif
%ifarch ppc64le
  BUILD_PLATFORM="linux/ppc64le"
%endif
%ifarch %{arm} aarch64
  BUILD_PLATFORM="linux/arm64"
%endif
%ifarch s390x
  BUILD_PLATFORM="linux/s390x"
%endif

PREFIX=%{_builddir}  %{os_git_vars} make build
%endif
%endif

%install

PLATFORM="$(go env GOHOSTOS)/$(go env GOHOSTARCH)"
install -d %{buildroot}%{_bindir}

# Install linux components
for bin in containerd-stargz-grpc ctr-remote stargz-store
do
  echo "+++ INSTALLING ${bin}"
  install -p -m 755 $PWD/out/${bin} %{buildroot}%{_bindir}/${bin}
done

# EXAMPLE: Install tests
# install -d %{buildroot}%{_libexecdir}/%{name}
# install -p -m 755 _output/local/bin/${PLATFORM}/extended.test %{buildroot}%{_libexecdir}/%{name}/

# EXAMPLE: Install other files
# install -p -m 0755 _output/local/bin/${PLATFORM}/sdn-cni-plugin %{buildroot}/opt/cni/bin/openshift-sdn

%files
%doc README.md
%license LICENSE
%{_bindir}/containerd-stargz-grpc
%{_bindir}/ctr-remote
%{_bindir}/stargz-store

# EXAMPLE: Managing configuration
# %defattr(-,root,root,0700)
# %dir %config(noreplace) %{_sysconfdir}/origin
# %ghost %dir %config(noreplace) %{_sysconfdir}/origin
# %ghost %config(noreplace) %{_sysconfdir}/origin/.config_managed

%pre

%changelog
* Wed Sep 9 2024 Sai Ramesh Vanka <svanka@redhat.com> 0.0.1
- First version of the spec file.
